from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from generalist_vla_agent.utils.types import ActionCommand, EncodedObservation, Instruction


class BasePolicyBackend(ABC):
    @abstractmethod
    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        raise NotImplementedError


class HeuristicPolicyBackend(BasePolicyBackend):
    """Deterministic baseline backend for smoke tests and fast demos."""

    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        rgb_mean, depth_mean, _ = encoded_obs.feature_vector

        if instruction.intent == "pick_and_place":
            action_name = "move_to_target" if rgb_mean > 0.2 else "search_target"
            confidence = 0.67 if rgb_mean > 0.2 else 0.45
        elif instruction.intent == "navigate_or_move":
            action_name = "navigate_to_waypoint"
            confidence = 0.62
        else:
            action_name = "hold_position" if depth_mean > 0.5 else "scan_scene"
            confidence = 0.58

        return ActionCommand(
            name=action_name,
            confidence=confidence,
            params={
                "backend": "heuristic",
                "intent": instruction.intent,
                "entities": instruction.entities,
                "encoder_metadata": encoded_obs.metadata,
            },
        )


class TrainedIntentPolicyBackend(BasePolicyBackend):
    """
    Lightweight trained backend:
    maps parsed intent -> most frequent action from training artifacts.
    """

    def __init__(self, artifact_path: str | Path, fallback: BasePolicyBackend | None = None) -> None:
        self.artifact_path = Path(artifact_path)
        self.fallback = fallback or HeuristicPolicyBackend()
        self.intent_to_action: dict[str, str] = {}
        self.intent_to_confidence: dict[str, float] = {}
        self._load_artifact()

    def _load_artifact(self) -> None:
        if not self.artifact_path.exists():
            raise FileNotFoundError(
                f"Trained policy artifact not found: {self.artifact_path}. "
                "Run scripts/train.py first."
            )
        with self.artifact_path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)
        self.intent_to_action = payload.get("intent_to_action", {})
        self.intent_to_confidence = payload.get("intent_to_confidence", {})

    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        action_name = self.intent_to_action.get(instruction.intent)
        if not action_name:
            return self.fallback.predict(instruction, encoded_obs)

        confidence = float(self.intent_to_confidence.get(instruction.intent, 0.7))
        return ActionCommand(
            name=action_name,
            confidence=confidence,
            params={
                "backend": "trained_intent",
                "intent": instruction.intent,
                "entities": instruction.entities,
                "encoder_metadata": encoded_obs.metadata,
            },
        )


class TrainedTemporalPolicyBackend(BasePolicyBackend):
    """
    Lightweight temporal backend:
    maps (intent, prev_action) -> most frequent next action.
    Falls back to intent-only mapping, then heuristic.
    """

    def __init__(self, artifact_path: str | Path, fallback: BasePolicyBackend | None = None) -> None:
        self.artifact_path = Path(artifact_path)
        self.fallback = fallback or HeuristicPolicyBackend()
        self.intent_prev_to_action: dict[str, str] = {}
        self.intent_prev_to_confidence: dict[str, float] = {}
        self.intent_to_action: dict[str, str] = {}
        self._load_artifact()

    def _load_artifact(self) -> None:
        if not self.artifact_path.exists():
            raise FileNotFoundError(
                f"Temporal policy artifact not found: {self.artifact_path}. "
                "Run scripts/train.py with temporal backend first."
            )
        with self.artifact_path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)
        self.intent_prev_to_action = payload.get("intent_prev_to_action", {})
        self.intent_prev_to_confidence = payload.get("intent_prev_to_confidence", {})
        self.intent_to_action = payload.get("intent_to_action", {})

    def predict(self, instruction: Instruction, encoded_obs: EncodedObservation) -> ActionCommand:
        prev_action = str(instruction.context.get("prev_action", "<none>"))
        key = f"{instruction.intent}|{prev_action}"
        action_name = self.intent_prev_to_action.get(key)

        if not action_name:
            action_name = self.intent_to_action.get(instruction.intent)
        if not action_name:
            return self.fallback.predict(instruction, encoded_obs)

        confidence = float(
            self.intent_prev_to_confidence.get(key, 0.75 if key in self.intent_prev_to_action else 0.6)
        )
        return ActionCommand(
            name=action_name,
            confidence=confidence,
            params={
                "backend": "trained_temporal",
                "intent": instruction.intent,
                "prev_action": prev_action,
                "entities": instruction.entities,
                "encoder_metadata": encoded_obs.metadata,
            },
        )


def fit_intent_policy_artifact(samples: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for sample in samples:
        counts[sample["intent"]][sample["target_action"]] += 1

    intent_to_action: dict[str, str] = {}
    intent_to_confidence: dict[str, float] = {}
    for intent, counter in counts.items():
        action, freq = counter.most_common(1)[0]
        total = sum(counter.values())
        intent_to_action[intent] = action
        intent_to_confidence[intent] = round(freq / max(total, 1), 3)

    return {
        "intent_to_action": intent_to_action,
        "intent_to_confidence": intent_to_confidence,
        "num_samples": len(samples),
    }


def fit_temporal_policy_artifact(samples: list[dict[str, Any]]) -> dict[str, Any]:
    intent_prev_counts: dict[str, Counter[str]] = defaultdict(Counter)
    intent_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for sample in samples:
        intent = sample["intent"]
        prev_action = str(sample.get("prev_action", "<none>"))
        target_action = sample["target_action"]

        intent_prev_counts[f"{intent}|{prev_action}"][target_action] += 1
        intent_counts[intent][target_action] += 1

    intent_prev_to_action: dict[str, str] = {}
    intent_prev_to_confidence: dict[str, float] = {}
    for key, counter in intent_prev_counts.items():
        action, freq = counter.most_common(1)[0]
        total = sum(counter.values())
        intent_prev_to_action[key] = action
        intent_prev_to_confidence[key] = round(freq / max(total, 1), 3)

    intent_to_action: dict[str, str] = {}
    for intent, counter in intent_counts.items():
        intent_to_action[intent] = counter.most_common(1)[0][0]

    return {
        "intent_prev_to_action": intent_prev_to_action,
        "intent_prev_to_confidence": intent_prev_to_confidence,
        "intent_to_action": intent_to_action,
        "num_samples": len(samples),
    }
