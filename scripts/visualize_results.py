from __future__ import annotations

import argparse
from glob import glob
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent.utils.logging import build_logger
from generalist_vla_agent.visualization import build_dashboard


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build evaluation visualization dashboard.")
    parser.add_argument("--config", type=str, default="configs/visualize.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config_with_extends(args.config)
    logger = build_logger("visualize")

    report_glob = cfg["visualize"].get("reports_glob", "outputs/reports/*.json")
    html_out = Path(cfg["visualize"].get("output_html", "outputs/visuals/dashboard.html"))
    md_out = Path(cfg["visualize"].get("output_markdown", "outputs/visuals/leaderboard.md"))

    report_files = [Path(p) for p in glob(report_glob)]
    summary = build_dashboard(report_files=report_files, output_html=html_out, output_markdown=md_out)

    logger.info("Dashboard generated with %s reports", summary["num_reports"])
    logger.info("HTML: %s", summary["output_html"])
    logger.info("Markdown: %s", summary["output_markdown"])


if __name__ == "__main__":
    main()
