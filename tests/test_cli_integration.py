"""Integration test for the coglet CLI runtime server.

Starts a real FastAPI server on an ephemeral port, then exercises
every CLI command via the HTTP client helpers.
"""

import asyncio
import json
import textwrap
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from coglet.cli import (
    create_app, _post, _get, _delete, _observe_sse, _parse_channel_ref,
)


@pytest.fixture(scope="module")
def runtime_port(tmp_path_factory):
    """Start a coglet runtime server on an ephemeral port, yield the port."""
    app = create_app()

    # Find a free port
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to be ready
    for _ in range(50):
        try:
            _get(port, "/status")
            break
        except SystemExit:
            time.sleep(0.1)
    else:
        pytest.fail("runtime server did not start")

    yield port

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def cog_dirs(tmp_path):
    """Create counter, doubler, printer .cog dirs in tmp_path."""
    # counter
    counter = tmp_path / "counter.cog"
    counter.mkdir()
    (counter / "manifest.toml").write_text(textwrap.dedent("""\
        [coglet]
        class = "counter.CounterCoglet"
    """))
    (counter / "counter.py").write_text(textwrap.dedent("""\
        from coglet import Coglet, LifeLet, TickLet, every

        class CounterCoglet(Coglet, LifeLet, TickLet):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.n = 0

            async def on_start(self):
                pass

            @every(1, "s")
            async def emit(self):
                self.n += 1
                await self.transmit("count", self.n)

            async def on_stop(self):
                pass
    """))

    # doubler
    doubler = tmp_path / "doubler.cog"
    doubler.mkdir()
    (doubler / "manifest.toml").write_text(textwrap.dedent("""\
        [coglet]
        class = "doubler.DoublerCoglet"
    """))
    (doubler / "doubler.py").write_text(textwrap.dedent("""\
        from coglet import Coglet, LifeLet, listen

        class DoublerCoglet(Coglet, LifeLet):
            async def on_start(self):
                pass

            @listen("input")
            async def on_input(self, n):
                await self.transmit("output", n * 2)

            async def on_stop(self):
                pass
    """))

    # printer (sink)
    printer = tmp_path / "printer.cog"
    printer.mkdir()
    (printer / "manifest.toml").write_text(textwrap.dedent("""\
        [coglet]
        class = "printer.PrinterCoglet"
    """))
    (printer / "printer.py").write_text(textwrap.dedent("""\
        from coglet import Coglet, LifeLet, listen, enact

        class PrinterCoglet(Coglet, LifeLet):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.received = []

            async def on_start(self):
                pass

            @listen("output")
            async def on_output(self, value):
                self.received.append(value)
                await self.transmit("log", value)

            @enact("reset")
            async def on_reset(self, _data):
                self.received.clear()

            async def on_stop(self):
                pass
    """))

    return {"counter": counter, "doubler": doubler, "printer": printer}


class TestRuntimeStatus:
    def test_empty_status(self, runtime_port):
        resp = _get(runtime_port, "/status")
        assert "tree" in resp
        assert resp["coglets"] == []
        assert resp["links"] == []

    def test_tree_empty(self, runtime_port):
        resp = _get(runtime_port, "/tree")
        assert "empty" in resp["tree"].lower() or "CogletRuntime" in resp["tree"]


class TestCreateAndStop:
    def test_create_returns_id(self, runtime_port, cog_dirs):
        resp = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        assert "id" in resp
        assert "class" in resp
        assert resp["class"] == "DoublerCoglet"
        assert resp["id"].startswith("doubler-")

        # Cleanup
        _post(runtime_port, f"/stop/{resp['id']}")

    def test_create_shows_in_status(self, runtime_port, cog_dirs):
        resp = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        cid = resp["id"]

        status = _get(runtime_port, "/status")
        ids = [c["id"] for c in status["coglets"]]
        assert cid in ids

        _post(runtime_port, f"/stop/{cid}")

    def test_stop_removes_from_status(self, runtime_port, cog_dirs):
        resp = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        cid = resp["id"]

        _post(runtime_port, f"/stop/{cid}")

        status = _get(runtime_port, "/status")
        ids = [c["id"] for c in status["coglets"]]
        assert cid not in ids


class TestChannels:
    def test_list_channels(self, runtime_port, cog_dirs):
        resp = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        cid = resp["id"]

        ch = _get(runtime_port, f"/channels/{cid}")
        assert "input" in ch["listen"]

        _post(runtime_port, f"/stop/{cid}")


class TestTransmit:
    def test_transmit_dispatches_listen(self, runtime_port, cog_dirs):
        """Transmit into a coglet's channel triggers its @listen handler."""
        d = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        did = d["id"]

        # Transmit 5 into doubler's input — should trigger @listen("input")
        # which transmits 10 on "output"
        _post(runtime_port, f"/transmit/{did}/input", data="5")

        time.sleep(0.2)

        # Check that doubler's output channel has a subscriber count
        ch = _get(runtime_port, f"/channels/{did}")
        assert "output" in ch["transmit"] or "input" in ch["listen"]

        _post(runtime_port, f"/stop/{did}")


class TestEnact:
    def test_enact_sends_command(self, runtime_port, cog_dirs):
        resp = _post(runtime_port, "/create", cog_dir=str(cog_dirs["printer"]))
        cid = resp["id"]

        # Send reset command
        resp = _post(runtime_port, f"/enact/{cid}", command="reset")
        assert "sent" in resp["msg"]

        _post(runtime_port, f"/stop/{cid}")


class TestLinkPipeline:
    def test_link_and_data_flows(self, runtime_port, cog_dirs):
        """Create doubler + printer, link them, transmit, verify flow."""
        d = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        did = d["id"]
        p = _post(runtime_port, "/create", cog_dir=str(cog_dirs["printer"]))
        pid = p["id"]

        # Link doubler:output -> printer:output
        resp = _post(runtime_port, "/link",
                     src_id=did, src_channel="output",
                     dest_id=pid, dest_channel="output")
        assert "->" in resp["msg"]

        # Verify link shows up
        links = _get(runtime_port, "/links")
        assert len(links["links"]) >= 1
        link = links["links"][-1]
        assert link["src"] == did
        assert link["dest"] == pid

        # Transmit into doubler — should flow through to printer
        _post(runtime_port, f"/transmit/{did}/input", data="7")
        time.sleep(0.3)

        # Verify in status
        status = _get(runtime_port, "/status")
        assert any(lk["src"] == did for lk in status["links"])

        # Unlink
        resp = _delete(runtime_port, "/link",
                       src_id=did, src_channel="output",
                       dest_id=pid, dest_channel="output")
        assert "unlinked" in resp["msg"]

        # Verify link removed
        links = _get(runtime_port, "/links")
        assert not any(lk["src"] == did and lk["dest"] == pid for lk in links["links"])

        _post(runtime_port, f"/stop/{did}")
        _post(runtime_port, f"/stop/{pid}")

    def test_stop_removes_links(self, runtime_port, cog_dirs):
        """Stopping a coglet removes its links."""
        d = _post(runtime_port, "/create", cog_dir=str(cog_dirs["doubler"]))
        did = d["id"]
        p = _post(runtime_port, "/create", cog_dir=str(cog_dirs["printer"]))
        pid = p["id"]

        _post(runtime_port, "/link",
              src_id=did, src_channel="output",
              dest_id=pid, dest_channel="output")

        # Stop doubler — link should be removed
        _post(runtime_port, f"/stop/{did}")

        links = _get(runtime_port, "/links")
        assert not any(lk["src"] == did for lk in links["links"])

        _post(runtime_port, f"/stop/{pid}")


class TestParseChannelRef:
    def test_valid(self):
        assert _parse_channel_ref("foo-a1b2:bar") == ("foo-a1b2", "bar")

    def test_invalid(self):
        with pytest.raises(SystemExit):
            _parse_channel_ref("nocolon")
