"""Unit tests for coglet.channel: Channel, ChannelSubscription, ChannelBus."""
from __future__ import annotations

import asyncio

import pytest

from coglet.channel import Channel, ChannelBus, ChannelSubscription


# ---- Channel ----

@pytest.mark.asyncio
async def test_channel_put_get():
    ch = Channel()
    await ch.put("hello")
    result = await ch.get()
    assert result == "hello"


@pytest.mark.asyncio
async def test_channel_put_nowait():
    ch = Channel()
    ch.put_nowait("fast")
    result = await ch.get()
    assert result == "fast"


@pytest.mark.asyncio
async def test_channel_ordering():
    ch = Channel()
    for i in range(5):
        await ch.put(i)
    results = [await ch.get() for _ in range(5)]
    assert results == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_channel_aiter():
    ch = Channel()
    await ch.put("a")
    await ch.put("b")

    collected = []
    async for item in ch:
        collected.append(item)
        if len(collected) == 2:
            break
    assert collected == ["a", "b"]


@pytest.mark.asyncio
async def test_channel_maxsize():
    ch = Channel(maxsize=1)
    ch.put_nowait("first")
    with pytest.raises(asyncio.QueueFull):
        ch.put_nowait("second")


# ---- ChannelSubscription ----

@pytest.mark.asyncio
async def test_subscription_independence():
    """Each subscription has its own queue."""
    ch = Channel()
    sub1 = ch.subscribe()
    sub2 = ch.subscribe()

    # Subscriptions are separate from the main channel
    await ch.put("main")
    result = await ch.get()
    assert result == "main"

    # Subscriptions don't get the main channel data automatically
    # (they need to be fed by the ChannelBus)


@pytest.mark.asyncio
async def test_subscription_aiter():
    ch = Channel()
    sub = ch.subscribe()
    await sub._queue.put("x")
    await sub._queue.put("y")

    collected = []
    async for item in sub:
        collected.append(item)
        if len(collected) == 2:
            break
    assert collected == ["x", "y"]


# ---- ChannelBus ----

@pytest.mark.asyncio
async def test_bus_transmit_no_subscribers():
    """Transmit on a channel with no subscribers is a no-op."""
    bus = ChannelBus()
    await bus.transmit("empty", "data")  # should not raise


@pytest.mark.asyncio
async def test_bus_transmit_single_subscriber():
    bus = ChannelBus()
    sub = bus.subscribe("events")
    await bus.transmit("events", {"type": "click"})
    result = await sub.get()
    assert result == {"type": "click"}


@pytest.mark.asyncio
async def test_bus_transmit_multiple_subscribers():
    """All subscribers get the same data independently."""
    bus = ChannelBus()
    sub1 = bus.subscribe("data")
    sub2 = bus.subscribe("data")

    await bus.transmit("data", 42)

    r1 = await sub1.get()
    r2 = await sub2.get()
    assert r1 == 42
    assert r2 == 42


@pytest.mark.asyncio
async def test_bus_transmit_nowait():
    bus = ChannelBus()
    sub = bus.subscribe("fast")
    bus.transmit_nowait("fast", "sync-data")
    result = await sub.get()
    assert result == "sync-data"


@pytest.mark.asyncio
async def test_bus_multiple_channels():
    bus = ChannelBus()
    sub_a = bus.subscribe("alpha")
    sub_b = bus.subscribe("beta")

    await bus.transmit("alpha", "a-data")
    await bus.transmit("beta", "b-data")

    assert await sub_a.get() == "a-data"
    assert await sub_b.get() == "b-data"


@pytest.mark.asyncio
async def test_bus_ensure_channel_idempotent():
    bus = ChannelBus()
    ch1 = bus._ensure_channel("test")
    ch2 = bus._ensure_channel("test")
    assert ch1 is ch2


@pytest.mark.asyncio
async def test_bus_subscribe_creates_channel():
    bus = ChannelBus()
    assert "new" not in bus._channels
    bus.subscribe("new")
    assert "new" in bus._channels


@pytest.mark.asyncio
async def test_bus_transmit_ordering():
    bus = ChannelBus()
    sub = bus.subscribe("seq")
    for i in range(10):
        await bus.transmit("seq", i)
    results = [await sub.get() for _ in range(10)]
    assert results == list(range(10))
