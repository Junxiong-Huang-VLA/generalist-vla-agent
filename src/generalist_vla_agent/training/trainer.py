from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generalist_vla_agent.policy.backends import (
    fit_intent_policy_artifact,
    fit_temporal_policy_artifact,
)


def train_intent_policy(samples: list[dict[str, Any]], artifact_path: str | Path) -> dict[str, Any]:
    artifact = fit_intent_policy_artifact(samples=samples)
    out = Path(artifact_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fp:
        json.dump(artifact, fp, ensure_ascii=True, indent=2)
    return artifact


def train_temporal_policy(samples: list[dict[str, Any]], artifact_path: str | Path) -> dict[str, Any]:
    artifact = fit_temporal_policy_artifact(samples=samples)
    out = Path(artifact_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fp:
        json.dump(artifact, fp, ensure_ascii=True, indent=2)
    return artifact


def predict_action_from_intent_artifact(artifact: dict[str, Any], row: dict[str, Any]) -> str:
    return str(artifact.get("intent_to_action", {}).get(row["intent"], ""))


def predict_action_from_temporal_artifact(artifact: dict[str, Any], row: dict[str, Any]) -> str:
    intent = row["intent"]
    prev_action = str(row.get("prev_action", "<none>"))
    key = f"{intent}|{prev_action}"
    return str(
        artifact.get("intent_prev_to_action", {}).get(
            key,
            artifact.get("intent_to_action", {}).get(intent, ""),
        )
    )


def evaluate_artifact_accuracy(
    artifact: dict[str, Any],
    rows: list[dict[str, Any]],
    backend: str,
) -> dict[str, Any]:
    if not rows:
        return {"num_samples": 0, "action_accuracy": 0.0}

    correct = 0
    for row in rows:
        if backend == "trained_temporal":
            predicted = predict_action_from_temporal_artifact(artifact, row)
        else:
            predicted = predict_action_from_intent_artifact(artifact, row)
        if predicted == row["target_action"]:
            correct += 1

    return {
        "num_samples": len(rows),
        "action_accuracy": round(correct / len(rows), 4),
    }
