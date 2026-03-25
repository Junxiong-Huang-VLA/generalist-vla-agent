from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def build_release_summary(
    train_report_path: Path,
    eval_report_paths: list[Path],
    leaderboard_path: Path,
    dashboard_path: Path,
    output_path: Path,
) -> Path:
    train_report = _read_json(train_report_path) if train_report_path.exists() else {}
    eval_reports = [(_read_json(p), p.name) for p in eval_report_paths if p.exists()]

    lines = [
        "# Release Summary",
        "",
        f"- Generated at: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "## Training",
        "",
        f"- Backend: `{train_report.get('backend', 'unknown')}`",
        f"- Train samples: `{train_report.get('train_samples', 0)}`",
    ]
    if "val_metrics" in train_report:
        val = train_report["val_metrics"]
        lines.append(f"- Validation accuracy: `{val.get('action_accuracy', 0.0)}`")
    lines.extend(
        [
            "",
            "## Evaluation",
            "",
            "| Backend | Dataset | Episodes | Accuracy | Confidence | Source |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for report, name in eval_reports:
        lines.append(
            f"| {report.get('policy_backend', 'unknown')} | {report.get('dataset_kind', 'unknown')} | "
            f"{report.get('episodes', 0)} | {report.get('action_accuracy', 0.0):.4f} | "
            f"{report.get('mean_confidence', 0.0):.4f} | {name} |"
        )
        if "sequence_success_rate" in report:
            lines.append(
                f"|  |  |  | seq_success={report.get('sequence_success_rate', 0.0):.4f} | "
                f"seq_mean_acc={report.get('mean_sequence_accuracy', 0.0):.4f} |  |"
            )

    lines.extend(["", "## Error Analysis (Top Confusions)", ""])
    for report, name in eval_reports:
        confusions = report.get("top_confusions", [])
        if not confusions:
            lines.append(f"- `{name}`: no confusion entries (perfect or unavailable).")
            continue
        top = confusions[0]
        lines.append(
            f"- `{name}`: `{top.get('target')}` -> `{top.get('predicted')}` "
            f"(count={top.get('count', 0)})"
        )

    lines.extend(
        [
            "",
            "## Visualization Assets",
            "",
            f"- Dashboard: `{dashboard_path}`",
            f"- Leaderboard: `{leaderboard_path}`",
            "",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
