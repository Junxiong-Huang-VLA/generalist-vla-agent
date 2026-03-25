from pathlib import Path

from generalist_vla_agent.visualization.release import build_release_summary


def test_build_release_summary() -> None:
    base = Path("outputs/test_visuals/release")
    base.mkdir(parents=True, exist_ok=True)

    train = base / "train.json"
    train.write_text(
        '{"backend":"trained_temporal","train_samples":100,"val_metrics":{"action_accuracy":0.9}}',
        encoding="utf-8",
    )
    eval_a = base / "eval_a.json"
    eval_a.write_text(
        '{"policy_backend":"trained_temporal","dataset_kind":"synthetic_temporal","episodes":20,"action_accuracy":0.95,"mean_confidence":0.9}',
        encoding="utf-8",
    )
    leaderboard = base / "leaderboard.md"
    leaderboard.write_text("# lb", encoding="utf-8")
    dashboard = base / "dashboard.html"
    dashboard.write_text("<html></html>", encoding="utf-8")
    summary = base / "release_summary.md"

    out = build_release_summary(
        train_report_path=train,
        eval_report_paths=[eval_a],
        leaderboard_path=leaderboard,
        dashboard_path=dashboard,
        output_path=summary,
    )
    assert out.exists()
