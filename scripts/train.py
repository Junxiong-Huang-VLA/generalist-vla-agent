from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.data import (
    DatasetSchema,
    generate_synthetic_dataset,
    generate_synthetic_temporal_dataset,
    load_jsonl,
    save_jsonl,
    validate_rows,
)
from generalist_vla_agent.training import (
    evaluate_artifact_accuracy,
    train_intent_policy,
    train_temporal_policy,
)
from generalist_vla_agent.utils.logging import build_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Placeholder training entrypoint.")
    parser.add_argument("--config", type=str, default="configs/train.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config_with_extends(args.config)
    logger = build_logger("train")

    seed = int(config["runtime"].get("seed", 42))
    num_samples = int(config["train"].get("num_samples", 128))
    backend = str(config["train"].get("backend", "trained_intent")).strip().lower()
    dataset_output = Path(config["train"].get("dataset_output", "outputs/data/train.jsonl"))
    artifact_output = Path(config["train"].get("artifact_output", "outputs/models/policy.json"))
    dataset_path = config["train"].get("dataset_path")
    val_dataset_path = config["train"].get("val_dataset_path")
    report_output = Path(config["train"].get("report_output", "outputs/reports/train_report.json"))
    validate_schema = bool(config["train"].get("validate_schema", True))
    schema_mode = str(config["train"].get("schema_mode", "temporal" if backend == "trained_temporal" else "intent"))

    if dataset_path:
        rows = load_jsonl(dataset_path)
        logger.info("Loaded training dataset: %s (%s samples)", dataset_path, len(rows))
    elif backend == "trained_temporal":
        rows = generate_synthetic_temporal_dataset(num_samples=num_samples, seed=seed)
    else:
        rows = generate_synthetic_dataset(num_samples=num_samples, seed=seed)

    if not dataset_path:
        logger.info(
            "Generating synthetic dataset: samples=%s seed=%s backend=%s",
            num_samples,
            seed,
            backend,
        )
        save_jsonl(dataset_output, rows)
        logger.info("Saved dataset to %s", dataset_output)

    if validate_schema:
        validate_rows(rows, DatasetSchema(mode=schema_mode))
        logger.info("Training dataset schema validated: mode=%s samples=%s", schema_mode, len(rows))

    if backend == "trained_temporal":
        artifact = train_temporal_policy(samples=rows, artifact_path=artifact_output)
    elif backend == "trained_intent":
        artifact = train_intent_policy(samples=rows, artifact_path=artifact_output)
    else:
        raise ValueError(f"Unsupported train backend: {backend}")

    logger.info("Saved policy artifact to %s", artifact_output)
    logger.info("Artifact summary keys=%s", sorted(artifact.keys()))

    report = {
        "backend": backend,
        "train_samples": len(rows),
        "artifact_path": str(artifact_output),
    }
    if val_dataset_path:
        val_rows = load_jsonl(val_dataset_path)
        if validate_schema:
            validate_rows(val_rows, DatasetSchema(mode=schema_mode))
        val_metrics = evaluate_artifact_accuracy(artifact=artifact, rows=val_rows, backend=backend)
        report["val_metrics"] = val_metrics
        logger.info("Validation metrics: %s", val_metrics)

    report_output.parent.mkdir(parents=True, exist_ok=True)
    with report_output.open("w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=True, indent=2)
    logger.info("Saved train report to %s", report_output)


if __name__ == "__main__":
    main()
