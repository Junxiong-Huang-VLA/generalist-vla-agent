from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.data import DatasetSchema, load_jsonl, validate_rows
from generalist_vla_agent.utils.logging import build_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate dataset schema.")
    parser.add_argument("--config", type=str, default="configs/validate_dataset.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config_with_extends(args.config)
    logger = build_logger("validate_dataset")

    dataset_path = cfg["validate"]["dataset_path"]
    schema_mode = cfg["validate"].get("schema_mode", "intent")
    rows = load_jsonl(dataset_path)
    validate_rows(rows, DatasetSchema(mode=schema_mode))
    logger.info("Dataset is valid: path=%s rows=%s mode=%s", dataset_path, len(rows), schema_mode)


if __name__ == "__main__":
    main()
