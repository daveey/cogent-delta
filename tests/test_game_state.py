"""Tests for GameState raw state container."""

from __future__ import annotations


def test_import():
    """GameState can be imported."""
    from cvc.game_state import GameState  # noqa: F401


def test_elements_round_robin():
    """Resource bias follows ELEMENTS[agent_id % 4]."""
    from cvc.game_state import _ELEMENTS, GameState
    from unittest.mock import MagicMock

    for agent_id in range(8):
        pei = MagicMock()
        pei.action_names = ["noop", "move_up"]
        pei.vibe_action_names = ["vibe_up"]
        gs = GameState(pei, agent_id=agent_id)
        assert gs.resource_bias == _ELEMENTS[agent_id % len(_ELEMENTS)], (
            f"agent_id={agent_id}: expected {_ELEMENTS[agent_id % len(_ELEMENTS)]}, "
            f"got {gs.resource_bias}"
        )


def test_reset_clears_state():
    """reset() zeroes all mutable state fields."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["noop", "move_up"]
    pei.vibe_action_names = ["vibe_up"]
    gs = GameState(pei, agent_id=2)

    # Mutate state to non-default values
    gs.step_index = 42
    gs.stalled_steps = 5
    gs.oscillation_steps = 3
    gs.explore_index = 7
    gs.last_global_pos = (10, 20)
    gs.last_inventory_signature = (("carbon", 5),)
    gs.temp_blocks[(1, 1)] = 99
    gs.junctions[(2, 2)] = ("up", 10)
    gs.current_target_position = (3, 3)
    gs.current_target_kind = "junction"
    gs.claimed_target = (4, 4)
    gs.sticky_target_position = (5, 5)
    gs.sticky_target_kind = "extractor"
    gs.claims[(6, 6)] = (0, 0)
    gs.events.append("fake_event")
    gs.role = "aligner"
    gs.resource_bias = "oxygen"

    gs.reset()

    assert gs.step_index == 0
    assert gs.stalled_steps == 0
    assert gs.oscillation_steps == 0
    assert gs.explore_index == 0
    assert gs.last_global_pos is None
    assert gs.last_inventory_signature is None
    assert gs.mg_state is None
    assert gs.previous_state is None
    assert len(gs.temp_blocks) == 0
    assert len(gs.junctions) == 0
    assert gs.current_target_position is None
    assert gs.current_target_kind is None
    assert gs.claimed_target is None
    assert gs.sticky_target_position is None
    assert gs.sticky_target_kind is None
    assert len(gs.claims) == 0
    assert len(gs.events) == 0
    assert gs.role == "miner"
    # Resource bias should be reset to default for agent_id=2
    assert gs.resource_bias == "germanium"


def test_fallback_action_noop():
    """Fallback is 'noop' when available."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["move_up", "noop"]
    pei.vibe_action_names = []
    gs = GameState(pei, agent_id=0)
    assert gs.fallback == "noop"


def test_fallback_action_first():
    """Fallback is first action when 'noop' not available."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["move_up", "move_down"]
    pei.vibe_action_names = []
    gs = GameState(pei, agent_id=0)
    assert gs.fallback == "move_up"
