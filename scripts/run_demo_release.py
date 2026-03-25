from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.utils.logging import build_logger
from generalist_vla_agent.visualization import build_release_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-to-end demo and build release summary.")
    parser.add_argument("--config", type=str, default="configs/demo_release.yaml")
    return parser.parse_args()


def _run_cmd(cmd: list[str], logger) -> None:
    logger.info("Running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    args = parse_args()
    cfg = load_config_with_extends(args.config)
    logger = build_logger("demo_release")

    steps = cfg["demo"]["steps"]
    for step in steps:
        _run_cmd(step["cmd"], logger)

    train_report = Path(cfg["demo"]["train_report"])
    eval_reports = [Path(x) for x in cfg["demo"]["eval_reports"]]
    leaderboard = Path(cfg["demo"]["leaderboard"])
    dashboard = Path(cfg["demo"]["dashboard"])
    summary_out = Path(cfg["demo"]["summary_out"])

    out = build_release_summary(
        train_report_path=train_report,
        eval_report_paths=eval_reports,
        leaderboard_path=leaderboard,
        dashboard_path=dashboard,
        output_path=summary_out,
    )
    logger.info("Release summary generated: %s", out)


if __name__ == "__main__":
    main()
