from pathlib import Path

from generalist_vla_agent.utils.config_profile import restore_profile, snapshot_profile


def test_snapshot_and_restore_profile() -> None:
    root = Path("outputs/test_profiles/root")
    root.mkdir(parents=True, exist_ok=True)
    cfg = root / "configs" / "sample.yaml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("a: 1\n", encoding="utf-8")

    profile = Path("outputs/test_profiles/lock_profile")
    manifest = snapshot_profile(files=[Path("configs/sample.yaml")], profile_dir=profile, root_dir=root)
    assert manifest.exists()

    cfg.write_text("a: 2\n", encoding="utf-8")
    restore_profile(profile_dir=profile, root_dir=root)
    assert cfg.read_text(encoding="utf-8").strip() == "a: 1"
