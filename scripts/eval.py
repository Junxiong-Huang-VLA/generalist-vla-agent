from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.data import (
    generate_synthetic_dataset,
    generate_synthetic_temporal_dataset,
    load_jsonl,
)
from generalist_vla_agent.utils.logging import build_logger
from generalist_vla_agent.utils.types import Observation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Placeholder evaluation entrypoint.")
    parser.add_argument("--config", type=str, default="configs/eval.yaml")
    parser.add_argument("--report-path", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config_with_extends(args.config)
    logger = build_logger("eval")

    seed = int(config["runtime"].get("seed", 42))
    episodes = int(config["eval"]["num_episodes"])
    dataset_kind = str(config["eval"].get("dataset_kind", "synthetic_intent"))
    dataset_path = config["eval"].get("dataset_path")
    intent_hint_mode = str(config["eval"].get("intent_hint_mode", "weak")).strip().lower()

    if dataset_path:
        rows = load_jsonl(dataset_path)
        episodes = len(rows)
    elif dataset_kind == "synthetic_temporal":
        rows = generate_synthetic_temporal_dataset(num_samples=episodes, seed=seed + 7)
    else:
        rows = generate_synthetic_dataset(num_samples=episodes, seed=seed + 7)

    agent = GeneralistVLAAgent.from_config(config)
    correct = 0
    confidence_sum = 0.0
    action_total: dict[str, int] = defaultdict(int)
    action_correct: dict[str, int] = defaultdict(int)
    confusion: Counter[tuple[str, str]] = Counter()
    seq_total: dict[str, int] = defaultdict(int)
    seq_correct: dict[str, int] = defaultdict(int)

    for row in rows:
        observation = Observation(
            rgb=row["observation"]["rgb"],
            depth=row["observation"]["depth"],
            text=row["observation"].get("text", ""),
        )
        context = {}
        if "prev_action" in row:
            context["prev_action"] = row["prev_action"]
        if "intent" in row and intent_hint_mode in {"weak", "strict"}:
            context["intent_hint"] = row["intent"]
            context["intent_hint_mode"] = intent_hint_mode

        result = agent.step(
            instruction_text=row["instruction"],
            observation=observation,
            context=context,
        )
        predicted = str(result["action_name"])
        target = str(row["target_action"])
        sequence_id = str(row.get("sequence_id", f"seq_{len(seq_total):06d}"))
        seq_total[sequence_id] += 1
        action_total[target] += 1
        if predicted == target:
            correct += 1
            action_correct[target] += 1
            seq_correct[sequence_id] += 1
        else:
            confusion[(target, predicted)] += 1
        confidence_sum += float(result["confidence"])

    action_accuracy = correct / max(episodes, 1)
    mean_confidence = confidence_sum / max(episodes, 1)
    if seq_total:
        sequence_success = sum(
            1 for sid, total in seq_total.items() if seq_correct.get(sid, 0) == total
        ) / len(seq_total)
        mean_sequence_accuracy = sum(
            seq_correct.get(sid, 0) / max(total, 1) for sid, total in seq_total.items()
        ) / len(seq_total)
    else:
        sequence_success = 0.0
        mean_sequence_accuracy = 0.0

    logger.info(
        "episodes=%s action_accuracy=%.2f seq_success=%.2f mean_confidence=%.2f",
        episodes,
        action_accuracy,
        sequence_success,
        mean_confidence,
    )

    report_path = args.report_path or config["eval"].get("report_path")
    if report_path:
        out = Path(report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "episodes": episodes,
            "dataset_kind": dataset_kind,
            "action_accuracy": round(action_accuracy, 4),
            "sequence_success_rate": round(sequence_success, 4),
            "mean_sequence_accuracy": round(mean_sequence_accuracy, 4),
            "mean_confidence": round(mean_confidence, 4),
            "policy_backend": config.get("policy", {}).get("backend", "heuristic"),
            "intent_hint_mode": intent_hint_mode,
            "per_action_accuracy": {
                action: round(action_correct[action] / total, 4)
                for action, total in sorted(action_total.items())
            },
            "top_confusions": [
                {"target": t, "predicted": p, "count": c}
                for (t, p), c in confusion.most_common(10)
            ],
        }
        with out.open("w", encoding="utf-8") as fp:
            json.dump(report, fp, ensure_ascii=True, indent=2)
        logger.info("Saved evaluation report to %s", out)


if __name__ == "__main__":
    main()
