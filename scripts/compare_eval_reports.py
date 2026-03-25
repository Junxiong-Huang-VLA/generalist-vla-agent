from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two eval reports.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", default="outputs/reports/eval_comparison.json")
    return parser.parse_args()


def _load(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as fp:
        return json.load(fp)


def main() -> None:
    args = parse_args()
    b = _load(args.baseline)
    c = _load(args.candidate)

    out = {
        "baseline": args.baseline,
        "candidate": args.candidate,
        "delta_action_accuracy": round(c.get("action_accuracy", 0.0) - b.get("action_accuracy", 0.0), 4),
        "delta_mean_confidence": round(c.get("mean_confidence", 0.0) - b.get("mean_confidence", 0.0), 4),
        "baseline_accuracy": b.get("action_accuracy", 0.0),
        "candidate_accuracy": c.get("action_accuracy", 0.0),
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=True, indent=2)
    print(json.dumps(out, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
