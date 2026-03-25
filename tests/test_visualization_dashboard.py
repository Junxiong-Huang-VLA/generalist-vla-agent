from pathlib import Path

from generalist_vla_agent.visualization.dashboard import build_dashboard


def test_build_dashboard_outputs_files() -> None:
    report = Path("outputs/test_visuals/eval.json")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        (
            '{"episodes": 10, "dataset_kind": "synthetic_intent", '
            '"action_accuracy": 0.8, "mean_confidence": 0.7, '
            '"policy_backend": "trained_intent"}'
        ),
        encoding="utf-8",
    )
    html_out = report.parent / "dashboard.html"
    md_out = report.parent / "leaderboard.md"

    summary = build_dashboard([report], html_out, md_out)
    assert summary["num_reports"] == 1
    assert html_out.exists()
    assert md_out.exists()
