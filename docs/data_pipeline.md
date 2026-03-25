# Data Pipeline

## Goal

Provide a deterministic local pipeline for building train/val/test datasets before model integration.

## Steps

1. Prepare split datasets:
   - `python scripts/prepare_data.py --config configs/data_prepare.yaml`
2. Validate dataset schema:
   - `python scripts/validate_dataset.py --config configs/validate_dataset.yaml`
3. Train from split training set:
   - `python scripts/train.py --config configs/train_temporal_from_split.yaml`
4. Evaluate on split test set:
   - `python scripts/eval.py --config configs/eval_temporal_from_split.yaml`

## Artifacts

- `outputs/data/splits_temporal/train.jsonl`
- `outputs/data/splits_temporal/val.jsonl`
- `outputs/data/splits_temporal/test.jsonl`
- `outputs/models/temporal_policy_from_split.json`
- `outputs/reports/train_temporal_from_split_report.json`
- `outputs/reports/eval_temporal_from_split.json`
