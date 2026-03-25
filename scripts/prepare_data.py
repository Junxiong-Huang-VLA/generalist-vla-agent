from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.data import (
    SplitSpec,
    generate_synthetic_dataset,
    generate_synthetic_temporal_dataset,
    save_jsonl,
    split_rows,
)
from generalist_vla_agent.utils.logging import build_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare train/val/test datasets.")
    parser.add_argument("--config", type=str, default="configs/data_prepare.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config_with_extends(args.config)
    logger = build_logger("prepare_data")

    seed = int(cfg["runtime"].get("seed", 42))
    num_samples = int(cfg["data"]["num_samples"])
    dataset_kind = str(cfg["data"].get("dataset_kind", "synthetic_intent"))
    output_dir = Path(cfg["data"].get("output_dir", "outputs/data/splits"))

    if dataset_kind == "synthetic_temporal":
        rows = generate_synthetic_temporal_dataset(num_samples=num_samples, seed=seed)
    else:
        rows = generate_synthetic_dataset(num_samples=num_samples, seed=seed)

    split_cfg = cfg["data"].get("splits", {})
    splits = split_rows(
        rows,
        spec=SplitSpec(
            train_ratio=float(split_cfg.get("train", 0.8)),
            val_ratio=float(split_cfg.get("val", 0.1)),
            test_ratio=float(split_cfg.get("test", 0.1)),
        ),
        seed=seed,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    for split_name, split_rows_data in splits.items():
        out = output_dir / f"{split_name}.jsonl"
        save_jsonl(out, split_rows_data)
        logger.info("%s: %s samples -> %s", split_name, len(split_rows_data), out)


if __name__ == "__main__":
    main()
