# Architecture Notes

## Design Goals

- decouple model-agnostic pipeline stages
- make each module replaceable without global rewrites
- support simulator-first and robot-first backends

## Current MVP Data Flow

1. Natural language instruction enters `InstructionParser`.
2. RGB-D-text observation enters `MultimodalEncoder`.
3. `PolicyPipeline` dispatches to selected policy backend (`heuristic` or `trained_intent`).
4. `ActionInterface` executes command (currently dry-run backend).
5. `EvalHookManager` receives execution result for metrics hooks.

## Training Loop (0->1)

1. Build synthetic dataset with `generate_synthetic_dataset`.
2. Train intent-action mapping artifact via `train_intent_policy`.
3. Save artifact (`outputs/models/intent_policy.json`).
4. Load artifact through config (`policy.backend=trained_intent`) for infer/eval.

## Planned Interface Stability

- `Instruction` / `Observation` / `ActionCommand` remain stable contracts.
- model-specific complexity should live in policy backends.
- evaluation logic should remain side-effect free and hook-driven.
