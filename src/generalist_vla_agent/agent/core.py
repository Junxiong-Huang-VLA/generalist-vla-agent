from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from generalist_vla_agent.actions.interface import ActionInterface, DryRunActionInterface
from generalist_vla_agent.actions.postprocess import ActionPostprocessor, RuleBasedActionCalibrator
from generalist_vla_agent.agent.instruction import InstructionParser
from generalist_vla_agent.eval.hooks import EvalHookManager
from generalist_vla_agent.perception.encoder import MultimodalEncoder
from generalist_vla_agent.policy.pipeline import PolicyPipeline
from generalist_vla_agent.policy.registry import build_policy_backend
from generalist_vla_agent.utils.types import ActionCommand, Observation


@dataclass
class GeneralistVLAAgent:
    parser: InstructionParser
    encoder: MultimodalEncoder
    policy: PolicyPipeline
    action_interface: ActionInterface
    eval_hooks: EvalHookManager
    postprocessor: ActionPostprocessor | None = None

    @classmethod
    def from_defaults(cls) -> "GeneralistVLAAgent":
        return cls(
            parser=InstructionParser(),
            encoder=MultimodalEncoder(),
            policy=PolicyPipeline(),
            action_interface=DryRunActionInterface(),
            eval_hooks=EvalHookManager(),
            postprocessor=None,
        )

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "GeneralistVLAAgent":
        policy_cfg = config.get("policy", {})
        backend_name = policy_cfg.get("backend", "heuristic")
        backend_kwargs = policy_cfg.get("backend_kwargs", {})

        backend = build_policy_backend(name=backend_name, kwargs=backend_kwargs)
        return cls(
            parser=InstructionParser(),
            encoder=MultimodalEncoder(),
            policy=PolicyPipeline(backend=backend),
            action_interface=DryRunActionInterface(),
            eval_hooks=EvalHookManager(),
            postprocessor=_build_postprocessor(config),
        )

    def infer(
        self,
        instruction_text: str,
        observation: Observation,
        context: dict[str, Any] | None = None,
    ) -> ActionCommand:
        parsed_instruction = self.parser.parse(instruction_text, context=context)
        encoded_obs = self.encoder.encode(observation)
        action = self.policy.predict(parsed_instruction, encoded_obs)
        if self.postprocessor is not None:
            action = self.postprocessor.apply(action, parsed_instruction, context=context)
        return action

    def step(
        self,
        instruction_text: str,
        observation: Observation,
        context: dict[str, Any] | None = None,
    ) -> dict:
        action = self.infer(instruction_text, observation, context=context)
        result = self.action_interface.execute(action)
        self.eval_hooks.run(action, result)
        return result


def _build_postprocessor(config: dict[str, Any]) -> ActionPostprocessor | None:
    pp_cfg = config.get("postprocess", {})
    enabled = bool(pp_cfg.get("enabled", False))
    if not enabled:
        return None
    mode = str(pp_cfg.get("mode", "rule_based")).strip().lower()
    if mode == "rule_based":
        return RuleBasedActionCalibrator(
            enable_gripper_close_fix=bool(pp_cfg.get("enable_gripper_close_fix", True))
        )
    raise ValueError(f"Unsupported postprocess mode: {mode}")
