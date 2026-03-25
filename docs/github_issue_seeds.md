# GitHub Issue Seeds

Use these to bootstrap the first public issue board.

## 1) Add EpisodeDataset abstraction

- **Title**: `feat(data): add EpisodeDataset with versioned schema loader`
- **Labels**: `enhancement`, `data`
- **Done when**:
  - supports train/val/test manifests
  - validates required fields and version
  - has unit tests for invalid samples

## 2) Sequence-level metrics expansion

- **Title**: `feat(eval): add sequence edit distance and step-F1`
- **Labels**: `enhancement`, `evaluation`
- **Done when**:
  - metrics included in `eval` report json
  - benchmark table includes new columns
  - docs updated with metric definitions

## 3) OpenVLA real backend path

- **Title**: `feat(policy): implement openvla_adapter checkpoint forward path`
- **Labels**: `enhancement`, `policy`, `vla`
- **Done when**:
  - loads checkpoint/tokenizer
  - produces action outputs via adapter
  - fallback behavior documented

## 4) RT-style adapter scaffold

- **Title**: `feat(policy): add rt_style backend with action chunk decoding`
- **Labels**: `enhancement`, `policy`
- **Done when**:
  - backend selectable via config
  - chunked actions decoded in pipeline
  - tests cover chunk edge cases

## 5) Real dataset onboarding checklist

- **Title**: `docs(data): add reproducible onboarding guide for large datasets`
- **Labels**: `documentation`, `data`
- **Done when**:
  - storage prerequisites documented
  - resume download strategy documented
  - sanity-check commands included

## 6) Config profile drift gate in CI

- **Title**: `feat(ci): add config profile drift check job`
- **Labels**: `enhancement`, `ci`
- **Done when**:
  - CI runs `compare_config_profile.py`
  - fails on missing/changed locked files
  - docs include override instructions

## 7) Benchmark publishing workflow

- **Title**: `feat(visualization): publish benchmark markdown as release artifact`
- **Labels**: `enhancement`, `visualization`
- **Done when**:
  - CI uploads `benchmark_table.md`
  - release summary links benchmark artifact
  - generated assets remain deterministic

## 8) Data conversion performance

- **Title**: `perf(data): speed up CALVIN conversion and split generation`
- **Labels**: `performance`, `data`
- **Done when**:
  - conversion runtime benchmark added
  - performance regression test or threshold documented
  - no schema regressions
