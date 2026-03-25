from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run intent_hint_mode ablation for eval configs.")
    parser.add_argument("--config-off", default="configs/eval_temporal_calvin_small_off.yaml")
    parser.add_argument("--config-weak", default="configs/eval_temporal_calvin_small_weak.yaml")
    parser.add_argument("--config-strict", default="configs/eval_temporal_calvin_small_strict.yaml")
    parser.add_argument("--output", default="outputs/reports/intent_hint_ablation_small.json")
    return parser.parse_args()


def _run_eval(config_path: str) -> dict:
    subprocess.run(["python", "scripts/eval.py", "--config", config_path], check=True)
    cfg = Path(config_path)
    name = cfg.stem
    report_name = name.replace("eval_", "eval_") + ".json"
    report_path = Path("outputs/reports") / report_name
    with report_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def main() -> None:
    args = parse_args()
    reports = {
        "off": _run_eval(args.config_off),
        "weak": _run_eval(args.config_weak),
        "strict": _run_eval(args.config_strict),
    }
    summary = {
        mode: {
            "action_accuracy": r.get("action_accuracy", 0.0),
            "mean_confidence": r.get("mean_confidence", 0.0),
        }
        for mode, r in reports.items()
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, ensure_ascii=True, indent=2)
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
