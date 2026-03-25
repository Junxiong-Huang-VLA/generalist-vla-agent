# Visualization

## Goal

Generate a shareable local dashboard from evaluation report JSON files.

## Command

```bash
python scripts/visualize_results.py --config configs/visualize.yaml
```

## Inputs

- `outputs/reports/*.json`

Only files with `action_accuracy` are treated as evaluation reports.

## Outputs

- `outputs/visuals/dashboard.html`
- `outputs/visuals/leaderboard.md`

## Use Cases

- attach leaderboard snapshots in GitHub releases
- compare policy backend iterations quickly
- maintain a reproducible local benchmark summary
