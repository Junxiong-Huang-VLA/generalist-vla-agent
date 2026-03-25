from __future__ import annotations

from dataclasses import replace
from typing import Any

from generalist_vla_agent.utils.types import ActionCommand, Instruction


class ActionPostprocessor:
    def apply(
        self,
        action: ActionCommand,
        instruction: Instruction,
        context: dict[str, Any] | None = None,
    ) -> ActionCommand:
        _ = instruction
        _ = context
        return action


class RuleBasedActionCalibrator(ActionPostprocessor):
    """
    Lightweight rule calibrator for common confusion cases.
    Rules are intentionally explicit and auditable.
    """

    def __init__(self, enable_gripper_close_fix: bool = True) -> None:
        self.enable_gripper_close_fix = enable_gripper_close_fix

    def apply(
        self,
        action: ActionCommand,
        instruction: Instruction,
        context: dict[str, Any] | None = None,
    ) -> ActionCommand:
        ctx = context or {}

        if (
            self.enable_gripper_close_fix
            and action.name == "hold_position"
            and (
                (
                    instruction.intent in {"manipulate", "pick_and_place"}
                    and str(ctx.get("prev_action", "")) in {"gripper_open", "move_to_target"}
                )
                or (
                    instruction.intent == "navigate_or_move"
                    and str(ctx.get("prev_action", "")) == "gripper_close"
                )
            )
        ):
            new_params = dict(action.params)
            new_params["calibrated_from"] = action.name
            new_params["calibrator_rule"] = "gripper_close_fix_v1"
            return replace(action, name="gripper_close", confidence=max(action.confidence, 0.82), params=new_params)

        return action
