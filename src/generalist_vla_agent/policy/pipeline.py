from __future__ import annotations

from generalist_vla_agent.policy.backends import BasePolicyBackend, HeuristicPolicyBackend
from generalist_vla_agent.utils.types import ActionCommand, EncodedObservation, Instruction


class PolicyPipeline:
    """Backend-driven policy pipeline ready for adapter extensions."""

    def __init__(self, backend: BasePolicyBackend | None = None) -> None:
        self.backend = backend or HeuristicPolicyBackend()

    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        return self.backend.predict(instruction, encoded_obs)
