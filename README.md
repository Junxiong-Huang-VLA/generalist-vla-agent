# generalist-vla-agent

Engineering-first Vision-Language-Action (VLA) starter repository for embodied AI.  
This project connects instruction understanding, multimodal observation encoding, policy inference, and action interface abstraction in a decoupled pipeline.

## Status Snapshot

- CI: passing (`.github/workflows/ci.yml`)
- Test suite: `15 passed`
- Lightweight CALVIN benchmark:
  - step accuracy: `1.0000`
  - sequence success: `1.0000`
  - mean confidence: `0.9850`

## Project Positioning

`generalist-vla-agent` is a practical baseline for teams building generalist embodied agents.  
It is designed as an extensible backbone rather than a one-off demo, with clean module boundaries for:

- instruction parsing
- multimodal observation encoding (RGB-D + language context)
- action interface abstraction
- policy pipeline orchestration
- evaluation hooks
- demo inference flow

## Target Users

- Embodied AI / Robotics researchers who need a reproducible engineering baseline
- Applied ML engineers integrating VLM/VLA models into robot stacks
- Open-source maintainers building long-term VLA repositories

## Core Features (MVP)

- Config-driven runtime (`configs/*.yaml`)
- Modular VLA pipeline under `src/generalist_vla_agent/*`
- Runnable train/infer/eval flow (`scripts/train.py`, `scripts/infer.py`, `scripts/eval.py`)
- Policy backend registry (`heuristic`, `trained_intent`)
- Synthetic dataset generator and JSONL pipeline
- Trainable intent-action artifact for zero-to-one experiments
- Temporal policy artifact with `prev_action` context
- Offline eval report export (`outputs/reports/*.json`)
- Dataset split preparation pipeline (`scripts/prepare_data.py`)
- Dataset schema validation (`scripts/validate_dataset.py`)
- OpenVLA adapter scaffold (`openvla_adapter` mock-ready)
- Baseline unit tests for pipeline sanity

## Architecture

```text
instruction
  -> InstructionParser
observation (rgb/depth/text)
  -> MultimodalEncoder
encoded state + parsed task
  -> PolicyPipeline
action command
  -> ActionInterface
evaluation hooks
  -> EvalHookManager
```

## Repository Structure

```text
generalist-vla-agent/
|- src/generalist_vla_agent/
|  |- agent/
|  |- perception/
|  |- policy/
|  |- actions/
|  |- eval/
|  |- data/
|  |- training/
|  |- visualization/
|  `- utils/
|- configs/
|- scripts/
|- tests/
|- docs/
`- .github/
```

## Quickstart

### 1) Install

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
```

### 2) Run Demo Inference

```bash
python scripts/infer.py --config configs/infer.yaml --instruction "Pick up the red cup and place it on the tray."
```

Expected output (example):

```text
action_name=move_to_target confidence=0.67 metadata={...}
```

### 3) Train a Minimal Policy Artifact (0->1)

```bash
python scripts/train.py --config configs/train.yaml
```

Then run trained inference:

```bash
python scripts/infer.py --config configs/infer_trained.yaml --instruction "Move to the blue marker near the wall."
```

Train temporal backend:

```bash
python scripts/train.py --config configs/train_temporal.yaml
python scripts/infer.py --config configs/infer_temporal.yaml --prev-action move_to_target
```

### 4) Prepare Split Datasets (train/val/test)

```bash
python scripts/prepare_data.py --config configs/data_prepare.yaml
python scripts/validate_dataset.py --config configs/validate_dataset.yaml
python scripts/train.py --config configs/train_temporal_from_split.yaml
```

### 5) Evaluate

```bash
python scripts/eval.py --config configs/eval.yaml
python scripts/eval.py --config configs/eval_trained.yaml
python scripts/eval.py --config configs/eval_temporal.yaml
python scripts/eval.py --config configs/eval_temporal_from_split.yaml
```

### 6) Run Tests

```bash
pytest
```

### 7) Build Visualization Dashboard

```bash
python scripts/visualize_results.py --config configs/visualize.yaml
```

Generated outputs:
- `outputs/visuals/dashboard.html`
- `outputs/visuals/leaderboard.md`

### 8) One-Command Demo Release

```bash
python scripts/run_demo_release.py --config configs/demo_release.yaml
```

Generated release asset:
- `outputs/visuals/release_summary.md`

Lightweight variant (smaller CALVIN subset):

```bash
python scripts/run_demo_release.py --config configs/demo_release_small.yaml
```

`demo_release_small` uses `intent_hint_mode=weak` as default for better confidence while keeping accuracy.

Generated release asset:
- `outputs/visuals/release_summary_small.md`

Intent hint mode ablation:

```bash
python scripts/run_intent_hint_ablation.py --output outputs/reports/intent_hint_ablation_small.json
```

Migrate legacy eval configs to default `intent_hint_mode=weak`:

```bash
python scripts/migrate_eval_intent_hint_mode.py --apply
```

Check drift against locked config profile:

```bash
python scripts/compare_config_profile.py --profile-dir configs/lock/default_weak_eval
```

Build benchmark table:

```bash
python scripts/build_benchmark_table.py --output outputs/visuals/benchmark_table.md
```

## Module Design

- `agent`: high-level orchestration and instruction parsing
- `perception`: multimodal observation preprocessing + encoding
- `policy`: policy pipeline abstraction, currently heuristic MVP
- `data`: synthetic dataset generation and JSONL IO
- `data/splits`: deterministic train/val/test splitting utilities
- `training`: policy artifact training utilities
- `training`: policy artifact training utilities + validation metrics output
- `actions`: environment/action interface contract
- `eval`: hook-based evaluation entrypoints and metrics stubs
- `utils`: shared config loading, typing, logging helpers

## Zero-to-One Workflow

1. Generate synthetic trajectories with instruction/intent/target_action.
2. Train intent or temporal policy artifact.
3. Load trained backend via config and run inference.
4. Evaluate action accuracy and export machine-readable reports.
5. Replace synthetic data/backend gradually with real datasets and VLA models.

## Extension Roadmap (VLA / OpenVLA / RT-style)

This repository is intentionally prepared for future model backends:

- VLA adapters:
  - Add `policy/backends/vla_transformer.py`
  - Map encoder outputs to model-specific tokens/features
- OpenVLA integration:
  - `openvla_adapter` scaffold is included and runnable in `dry_run_mock` mode
  - Next: connect checkpoint loader + tokenizer and batched trajectory inference
- RT-style policy support:
  - Add action chunking + temporal decoding in `policy/backends/rt_style.py`
  - Extend action interface for low-level control frequency and horizon

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).
Data pipeline details: [docs/data_pipeline.md](docs/data_pipeline.md).
Visualization details: [docs/visualization.md](docs/visualization.md).
CALVIN download notes: [docs/calvin_download.md](docs/calvin_download.md).
CALVIN integration: [docs/calvin_integration.md](docs/calvin_integration.md).
Config lock/restore: [docs/config_lock.md](docs/config_lock.md).
Issue seeding guide: [docs/github_issue_seeds.md](docs/github_issue_seeds.md).
Issue automation guide: [docs/github_issue_automation.md](docs/github_issue_automation.md).

## GitHub Metadata

- Description:
  - `Generalist Vision-Language-Action engineering scaffold for embodied AI with modular perception, policy, action, and evaluation pipelines.`
- Suggested Topics:
  - `embodied-ai`
  - `vision-language-action`
  - `robotics`
  - `multimodal`
  - `vla`
  - `openvla`
  - `rgbd`
  - `3d-vision`
  - `action-planning`
  - `robot-learning`
  - `mlops`
  - `python`

## Development Notes

- Keep interfaces stable and modules loosely coupled.
- Prefer adding new model backends behind adapter classes.
- Avoid leaking environment-specific logic into core policy interfaces.

## License

MIT
