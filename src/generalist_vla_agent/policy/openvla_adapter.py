from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from generalist_vla_agent.policy.backends import BasePolicyBackend, HeuristicPolicyBackend
from generalist_vla_agent.utils.types import ActionCommand, EncodedObservation, Instruction


@dataclass
class OpenVLAAdapterConfig:
    checkpoint_path: str = ""
    tokenizer_name: str = ""
    device: str = "cpu"
    dry_run_mock: bool = True


class OpenVLAAdapterBackend(BasePolicyBackend):
    """
    OpenVLA adapter scaffold.
    dry_run_mock=True keeps this backend runnable before model integration.
    """

    def __init__(self, cfg: OpenVLAAdapterConfig) -> None:
        self.cfg = cfg
        self.fallback = HeuristicPolicyBackend()
        self._validate_config()

    def _validate_config(self) -> None:
        if self.cfg.dry_run_mock:
            return
        if not self.cfg.checkpoint_path:
            raise ValueError("OpenVLA checkpoint_path is required when dry_run_mock is False")
        if not Path(self.cfg.checkpoint_path).exists():
            raise FileNotFoundError(f"OpenVLA checkpoint not found: {self.cfg.checkpoint_path}")

    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        if self.cfg.dry_run_mock:
            fallback_action = self.fallback.predict(instruction, encoded_obs)
            fallback_action.params["backend"] = "openvla_adapter_mock"
            fallback_action.params["openvla_device"] = self.cfg.device
            return fallback_action

        # Real integration point:
        # 1) tokenize language instruction
        # 2) encode multimodal features
        # 3) run OpenVLA checkpoint forward
        # 4) decode predicted action tokens/chunks
        raise NotImplementedError("OpenVLA real inference path is not implemented yet.")
