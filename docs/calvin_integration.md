# CALVIN Integration

## What Is Integrated

- Official CALVIN `debug` dataset conversion to project JSONL schema.
- Temporal train/val/test split generation.
- Training and evaluation configs that consume converted CALVIN data.

## Commands

```bash
python scripts/prepare_calvin_dataset.py --config configs/calvin_prepare.yaml
python scripts/train.py --config configs/train_temporal_calvin_debug.yaml
python scripts/eval.py --config configs/eval_temporal_calvin_debug.yaml
```

Intent hint ablation (small split):

```bash
python scripts/run_intent_hint_ablation.py \
  --config-off configs/eval_temporal_calvin_small_off.yaml \
  --config-weak configs/eval_temporal_calvin_small_weak.yaml \
  --config-strict configs/eval_temporal_calvin_small_strict.yaml \
  --output outputs/reports/intent_hint_ablation_small.json
```

## Outputs

- `outputs/data/calvin_debug_splits/train.jsonl`
- `outputs/data/calvin_debug_splits/val.jsonl`
- `outputs/data/calvin_debug_splits/test.jsonl`
- `outputs/models/temporal_policy_calvin_debug.json`
- `outputs/reports/train_temporal_calvin_debug_report.json`
- `outputs/reports/eval_temporal_calvin_debug.json`
