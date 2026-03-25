from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.data import DatasetSchema, save_jsonl, split_rows, validate_rows
from generalist_vla_agent.data.splits import SplitSpec
from generalist_vla_agent.utils.logging import build_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CALVIN dataset to project JSONL schema.")
    parser.add_argument("--config", type=str, default="configs/calvin_prepare.yaml")
    return parser.parse_args()


def _infer_action_label(rel_actions: np.ndarray) -> str:
    rel = np.asarray(rel_actions, dtype=float)
    if rel.shape[0] < 7:
        return "unknown_action"

    if abs(rel[6]) > 0.5:
        return "gripper_open" if rel[6] > 0 else "gripper_close"

    axis_names = ["move_x", "move_y", "move_z", "rot_roll", "rot_pitch", "rot_yaw"]
    idx = int(np.argmax(np.abs(rel[:6])))
    sign = "pos" if rel[idx] >= 0 else "neg"
    return f"{axis_names[idx]}_{sign}"


def _infer_intent_from_text(text: str) -> str:
    t = text.lower()
    if "open" in t or "close" in t or "turn" in t:
        return "manipulate"
    if "move" in t or "push" in t:
        return "navigate_or_move"
    if "pick" in t or "place" in t:
        return "pick_and_place"
    return "generic_task"


def _observation_summary(episode: dict[str, Any]) -> dict[str, list[float] | str]:
    rgb = episode["rgb_static"]
    depth = episode["depth_static"]
    rgb_mean = np.mean(rgb, axis=(0, 1)).astype(float).tolist()
    depth_mean = float(np.mean(depth))
    return {
        "rgb": [round(x / 255.0, 4) for x in rgb_mean],
        "depth": [round(depth_mean, 4)],
        "text": "calvin_static_rgbd",
    }


def _episode_file(root: Path, idx: int) -> Path:
    return root / f"episode_{idx:07d}.npz"


def main() -> None:
    args = parse_args()
    cfg = load_config_with_extends(args.config)
    logger = build_logger("prepare_calvin_dataset")

    root = Path(cfg["calvin_prepare"]["dataset_dir"])
    split_mode = str(cfg["calvin_prepare"].get("schema_mode", "temporal"))
    out_dir = Path(cfg["calvin_prepare"].get("output_dir", "outputs/data/calvin_debug_splits"))
    seed = int(cfg["runtime"].get("seed", 42))
    max_rows = int(cfg["calvin_prepare"].get("max_rows", 10000))

    lang_path = root / "training" / "lang_annotations" / "auto_lang_ann.npy"
    lang_obj = np.load(lang_path, allow_pickle=True).item()
    anns = lang_obj["language"]["ann"]
    tasks = lang_obj["language"]["task"]
    spans = lang_obj["info"]["indx"]

    rows: list[dict[str, Any]] = []
    for seq_num, (ann, task_name, span) in enumerate(zip(anns, tasks, spans)):
        start_idx, end_idx = int(span[0]), int(span[1])
        prev_action = "<none>"
        sequence_id = f"calvin_seq_{seq_num:06d}"
        for step_idx, ep_idx in enumerate(range(start_idx, end_idx + 1)):
            ep_file = _episode_file(root / "training", ep_idx)
            if not ep_file.exists():
                continue

            episode = np.load(ep_file, allow_pickle=True)
            action = _infer_action_label(episode["rel_actions"])
            row = {
                "sequence_id": sequence_id,
                "instruction": str(ann),
                "intent": _infer_intent_from_text(str(task_name)),
                "observation": _observation_summary(episode),
                "target_action": action,
            }
            if split_mode == "temporal":
                row["prev_action"] = prev_action
                row["step_index"] = step_idx
                prev_action = action

            rows.append(row)
            if len(rows) >= max_rows:
                break
        if len(rows) >= max_rows:
            break

    validate_rows(rows, DatasetSchema(mode=split_mode))
    logger.info("Converted CALVIN rows=%s mode=%s", len(rows), split_mode)

    split_cfg = cfg["calvin_prepare"].get("splits", {})
    splits = split_rows(
        rows,
        spec=SplitSpec(
            train_ratio=float(split_cfg.get("train", 0.8)),
            val_ratio=float(split_cfg.get("val", 0.1)),
            test_ratio=float(split_cfg.get("test", 0.1)),
        ),
        seed=seed,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    for split_name, split_rows_data in splits.items():
        out = out_dir / f"{split_name}.jsonl"
        save_jsonl(out, split_rows_data)
        logger.info("%s=%s -> %s", split_name, len(split_rows_data), out)


if __name__ == "__main__":
    main()
