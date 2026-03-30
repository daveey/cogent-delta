"""GameState: raw state container for CvC policy.

Holds all infrastructure state (world model, navigation counters, targeting
state) and handles observation processing.  No decision logic -- programs
handle all logic by reading/writing these public fields directly.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from mettagrid_sdk.games.cogsguard import CogsguardSemanticSurface
from mettagrid_sdk.sdk import MettagridState

from cvc.agent import helpers as _h
from cvc.agent.world_model import WorldModel
from mettagrid.policy.policy_env_interface import PolicyEnvInterface
from mettagrid.simulator.interface import AgentObservation

_COGSGUARD_SURFACE = CogsguardSemanticSurface()
_ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")
_TEMP_BLOCK_EXPIRE_STEPS = 10


class GameState:
    """Raw mutable state container -- one per agent per episode."""

    def __init__(
        self,
        policy_env_info: PolicyEnvInterface,
        *,
        agent_id: int,
        world_model: WorldModel | None = None,
    ) -> None:
        # Identity
        self.policy_env_info = policy_env_info
        self.agent_id = agent_id

        # Action validation
        self.action_names: set[str] = set(policy_env_info.action_names)
        self.vibe_actions: set[str] = set(policy_env_info.vibe_action_names)
        self.fallback: str = (
            "noop" if "noop" in self.action_names else policy_env_info.action_names[0]
        )

        # World model
        self.world_model: WorldModel = world_model or WorldModel()

        # Observation
        self.mg_state: MettagridState | None = None
        self.previous_state: MettagridState | None = None
        self.step_index: int = 0

        # Navigation
        self.last_global_pos: tuple[int, int] | None = None
        self.temp_blocks: dict[tuple[int, int], int] = {}
        self.stalled_steps: int = 0
        self.oscillation_steps: int = 0
        self.last_inventory_signature: tuple[tuple[str, int], ...] | None = None
        self.recent_navigation: deque[Any] = deque(maxlen=6)
        self.explore_index: int = 0

        # Junction memory
        self.junctions: dict[tuple[int, int], tuple[str | None, int]] = {}

        # Per-agent resource bias
        self.resource_bias: str = _ELEMENTS[agent_id % len(_ELEMENTS)]
        self.role: str = "miner"

        # Targeting (mutable by programs)
        self.current_target_position: tuple[int, int] | None = None
        self.current_target_kind: str | None = None
        self.claimed_target: tuple[int, int] | None = None
        self.sticky_target_position: tuple[int, int] | None = None
        self.sticky_target_kind: str | None = None
        self.claims: dict[tuple[int, int], tuple[int, int]] = {}

        # Events
        self.events: list[Any] = []

    # ── Observation processing ────────────────────────────────────────

    def process_obs(self, obs: AgentObservation) -> MettagridState:
        """Process a raw AgentObservation, updating all internal state.

        Returns the built MettagridState for downstream use.
        """
        self.step_index += 1

        state = _COGSGUARD_SURFACE.build_state_with_events(
            obs,
            policy_env_info=self.policy_env_info,
            step=self.step_index,
            previous_state=self.previous_state,
        )

        # Update world model
        self.world_model.update(state)
        current_pos = _h.absolute_position(state)
        self.world_model.prune_missing_extractors(
            current_position=current_pos,
            visible_entities=state.visible_entities,
            obs_width=self.policy_env_info.obs_width,
            obs_height=self.policy_env_info.obs_height,
        )

        # Update stall counter
        inv_sig = _h.inventory_signature(state)
        if (
            self.last_global_pos == current_pos
            and self.last_inventory_signature == inv_sig
        ):
            self.stalled_steps += 1
        else:
            self.stalled_steps = 0

        # Expire temp blocks older than threshold
        self.temp_blocks = {
            cell: until_step
            for cell, until_step in self.temp_blocks.items()
            if until_step >= self.step_index
        }

        # Reset per-tick targeting
        self.current_target_position = None
        self.current_target_kind = None

        # Collect events
        self.events.extend(state.recent_events)

        # Bookkeep for next tick
        self.previous_state = state
        self.last_global_pos = current_pos
        self.last_inventory_signature = inv_sig
        self.mg_state = state

        return state

    # ── Reset ─────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all state between episodes."""
        self.mg_state = None
        self.previous_state = None
        self.step_index = 0

        self.world_model.reset()

        self.last_global_pos = None
        self.temp_blocks.clear()
        self.stalled_steps = 0
        self.oscillation_steps = 0
        self.last_inventory_signature = None
        self.recent_navigation.clear()
        self.explore_index = 0

        self.junctions.clear()

        self.current_target_position = None
        self.current_target_kind = None
        self.claimed_target = None
        self.sticky_target_position = None
        self.sticky_target_kind = None
        self.claims.clear()

        self.events.clear()
        self.role = "miner"
        self.resource_bias = _ELEMENTS[self.agent_id % len(_ELEMENTS)]
