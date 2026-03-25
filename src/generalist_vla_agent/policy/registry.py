from __future__ import annotations

from pathlib import Path
from typing import Any

from generalist_vla_agent.policy.openvla_adapter import OpenVLAAdapterBackend, OpenVLAAdapterConfig
from generalist_vla_agent.policy.backends import (
    BasePolicyBackend,
    HeuristicPolicyBackend,
    TrainedIntentPolicyBackend,
    TrainedTemporalPolicyBackend,
)


def build_policy_backend(name: str, kwargs: dict[str, Any] | None = None) -> BasePolicyBackend:
    kwargs = kwargs or {}
    backend_name = name.strip().lower()

    if backend_name == "heuristic":
        return HeuristicPolicyBackend()
    if backend_name == "trained_intent":
        artifact_path = kwargs.get("artifact_path", "outputs/models/intent_policy.json")
        return TrainedIntentPolicyBackend(artifact_path=Path(artifact_path))
    if backend_name == "trained_temporal":
        artifact_path = kwargs.get("artifact_path", "outputs/models/temporal_policy.json")
        return TrainedTemporalPolicyBackend(artifact_path=Path(artifact_path))
    if backend_name == "openvla_adapter":
        cfg = OpenVLAAdapterConfig(
            checkpoint_path=str(kwargs.get("checkpoint_path", "")),
            tokenizer_name=str(kwargs.get("tokenizer_name", "")),
            device=str(kwargs.get("device", "cpu")),
            dry_run_mock=bool(kwargs.get("dry_run_mock", True)),
        )
        return OpenVLAAdapterBackend(cfg=cfg)
    raise ValueError(f"Unsupported policy backend: {name}")
