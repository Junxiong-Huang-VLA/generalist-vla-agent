from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build benchmark comparison markdown table.")
    parser.add_argument(
        "--reports",
        nargs="+",
        default=[
            "outputs/reports/eval_temporal_calvin_small.json",
            "outputs/reports/eval_temporal_calvin_debug.json",
            "outputs/reports/eval_temporal_from_split.json",
        ],
    )
    parser.add_argument("--output", default="outputs/visuals/benchmark_table.md")
    return parser.parse_args()


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def main() -> None:
    args = parse_args()
    rows = []
    for rp in args.reports:
        p = Path(rp)
        if not p.exists():
            continue
        r = _load(p)
        rows.append(
            {
                "name": p.name,
                "backend": r.get("policy_backend", "unknown"),
                "acc": float(r.get("action_accuracy", 0.0)),
                "seq": float(r.get("sequence_success_rate", r.get("action_accuracy", 0.0))),
                "seq_mean": float(r.get("mean_sequence_accuracy", r.get("action_accuracy", 0.0))),
                "conf": float(r.get("mean_confidence", 0.0)),
                "episodes": int(r.get("episodes", 0)),
            }
        )
    rows.sort(key=lambda x: (x["acc"], x["seq"], x["conf"]), reverse=True)

    lines = [
        "# Benchmark Table",
        "",
        "| Rank | Report | Backend | Episodes | Step Acc | Seq Success | Seq Mean Acc | Mean Conf |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for i, row in enumerate(rows, 1):
        lines.append(
            f"| {i} | {row['name']} | {row['backend']} | {row['episodes']} | "
            f"{row['acc']:.4f} | {row['seq']:.4f} | {row['seq_mean']:.4f} | {row['conf']:.4f} |"
        )
    if not rows:
        lines.append("| - | - | - | - | - | - | - | - |")
    lines.append("")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
