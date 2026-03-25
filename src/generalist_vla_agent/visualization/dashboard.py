from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


@dataclass
class EvalRecord:
    source_file: str
    backend: str
    action_accuracy: float
    mean_confidence: float
    episodes: int
    dataset_kind: str


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_records(report_files: list[Path]) -> list[EvalRecord]:
    records: list[EvalRecord] = []
    for report_file in report_files:
        with report_file.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)

        if "action_accuracy" not in payload:
            continue

        records.append(
            EvalRecord(
                source_file=report_file.name,
                backend=str(payload.get("policy_backend", "unknown")),
                action_accuracy=_safe_float(payload.get("action_accuracy")),
                mean_confidence=_safe_float(payload.get("mean_confidence")),
                episodes=_safe_int(payload.get("episodes")),
                dataset_kind=str(payload.get("dataset_kind", "unknown")),
            )
        )
    records.sort(key=lambda x: (x.action_accuracy, x.mean_confidence), reverse=True)
    return records


def _bar_svg(records: list[EvalRecord], width: int = 860, row_h: int = 42) -> str:
    if not records:
        return "<p>No evaluation reports found.</p>"

    left = 260
    bar_w = 500
    height = 28 + row_h * len(records)
    lines = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
    ]

    for idx, rec in enumerate(records):
        y = 20 + idx * row_h
        acc_width = int(max(0.0, min(1.0, rec.action_accuracy)) * bar_w)
        conf_width = int(max(0.0, min(1.0, rec.mean_confidence)) * bar_w)
        lines.append(f'<text x="10" y="{y + 16}" font-size="13" fill="#1f2937">{rec.backend}</text>')
        lines.append(
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="12" fill="#e5e7eb" rx="4" ry="4"/>'
        )
        lines.append(
            f'<rect x="{left}" y="{y}" width="{acc_width}" height="12" fill="#2563eb" rx="4" ry="4"/>'
        )
        lines.append(
            f'<rect x="{left}" y="{y + 14}" width="{bar_w}" height="10" fill="#e5e7eb" rx="4" ry="4"/>'
        )
        lines.append(
            f'<rect x="{left}" y="{y + 14}" width="{conf_width}" height="10" fill="#059669" rx="4" ry="4"/>'
        )
        lines.append(
            f'<text x="{left + bar_w + 8}" y="{y + 10}" font-size="11" fill="#2563eb">acc={rec.action_accuracy:.2f}</text>'
        )
        lines.append(
            f'<text x="{left + bar_w + 8}" y="{y + 24}" font-size="11" fill="#059669">conf={rec.mean_confidence:.2f}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def _to_markdown(records: list[EvalRecord], generated_at: str) -> str:
    lines = [
        "# Evaluation Leaderboard",
        "",
        f"- Generated at: `{generated_at}`",
        "",
        "| Rank | Backend | Accuracy | Confidence | Episodes | Dataset | Source |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for idx, rec in enumerate(records, 1):
        lines.append(
            f"| {idx} | {rec.backend} | {rec.action_accuracy:.4f} | {rec.mean_confidence:.4f} | {rec.episodes} | {rec.dataset_kind} | {rec.source_file} |"
        )
    if not records:
        lines.append("| - | - | - | - | - | - | - |")
    lines.append("")
    return "\n".join(lines)


def _to_html(records: list[EvalRecord], generated_at: str) -> str:
    rows = "\n".join(
        [
            (
                f"<tr><td>{idx}</td><td>{rec.backend}</td><td>{rec.action_accuracy:.4f}</td>"
                f"<td>{rec.mean_confidence:.4f}</td><td>{rec.episodes}</td>"
                f"<td>{rec.dataset_kind}</td><td>{rec.source_file}</td></tr>"
            )
            for idx, rec in enumerate(records, 1)
        ]
    )
    svg = _bar_svg(records)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>generalist-vla-agent Dashboard</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --line: #e2e8f0;
      --blue: #2563eb;
      --green: #059669;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: "Segoe UI", Arial, sans-serif; }}
    .wrap {{ max-width: 980px; margin: 28px auto; padding: 0 16px; }}
    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    h1 {{ font-size: 22px; margin: 0 0 10px; }}
    .meta {{ color: var(--muted); font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); text-align: left; padding: 8px 6px; }}
    th {{ background: #f1f5f9; }}
    .legend {{ font-size: 12px; color: var(--muted); margin-top: 8px; }}
    .sw {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>generalist-vla-agent Evaluation Dashboard</h1>
      <div class="meta">Generated at: {generated_at}</div>
      <div class="legend">
        <span class="sw" style="background: var(--blue)"></span>Action Accuracy
        <span style="display:inline-block; width: 12px;"></span>
        <span class="sw" style="background: var(--green)"></span>Mean Confidence
      </div>
      <div style="overflow-x:auto; margin-top: 8px;">{svg}</div>
    </div>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Rank</th><th>Backend</th><th>Accuracy</th><th>Confidence</th>
            <th>Episodes</th><th>Dataset</th><th>Source</th>
          </tr>
        </thead>
        <tbody>
          {rows if rows else "<tr><td colspan='7'>No reports found.</td></tr>"}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


def build_dashboard(
    report_files: list[Path],
    output_html: Path,
    output_markdown: Path,
) -> dict[str, Any]:
    records = _load_records(report_files)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_html.write_text(_to_html(records, generated_at), encoding="utf-8")
    output_markdown.write_text(_to_markdown(records, generated_at), encoding="utf-8")

    return {
        "num_reports": len(records),
        "output_html": str(output_html),
        "output_markdown": str(output_markdown),
    }
