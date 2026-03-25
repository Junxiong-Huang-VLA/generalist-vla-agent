# Config Lock and Restore

## Goal

Freeze known-good configuration files and restore them quickly when experiments drift.

## Create Snapshot

```bash
python scripts/lock_config_profile.py --profile-dir configs/lock/default_weak_eval
```

This writes:

- `configs/lock/default_weak_eval/manifest.json`
- copied config files under `configs/lock/default_weak_eval/configs/...`

## Restore Snapshot

```bash
python scripts/restore_config_profile.py --profile-dir configs/lock/default_weak_eval
```

This restores the locked config files into the working `configs/` directory.

## Recommended Workflow

1. After reaching a stable experiment baseline, run snapshot.
2. Before a risky config refactor, snapshot again to a new profile name.
3. If metrics regress or configs drift, run restore to recover instantly.
4. Run profile diff check anytime:

```bash
python scripts/compare_config_profile.py --profile-dir configs/lock/default_weak_eval
```
