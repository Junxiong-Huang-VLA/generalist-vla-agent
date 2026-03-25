# Roadmap

## v0.1 (Current)

- [x] modular project scaffold
- [x] config-driven MVP inference pipeline
- [x] abstract action interface + dry-run backend
- [x] policy backend registry (`heuristic`, `trained_intent`)
- [x] synthetic dataset + train artifact pipeline
- [x] action-accuracy based eval script
- [x] temporal policy backend (`trained_temporal`) with `prev_action` context
- [x] eval report export (`outputs/reports/*.json`)
- [x] deterministic dataset split pipeline (train/val/test)
- [x] dataset schema validation script and validators
- [x] split-aware training with validation metrics report
- [x] OpenVLA adapter scaffold with dry-run mock mode
- [x] CI workflow (tests + smoke pipeline)
- [x] baseline tests and docs

## v0.2

- [ ] dataset abstraction (`EpisodeDataset` class + versioned schema migration)
- [ ] richer observation adapters (image tensors, depth normalization)
- [ ] policy backend registry
- [ ] logging/experiment tracking integration

## v0.3

- [ ] OpenVLA adapter prototype
- [ ] RT-style action chunking adapter
- [ ] replay-based offline evaluation metrics
- [ ] benchmark runner with scenario configs

## v0.4+

- [ ] real robot action backend bridge (ROS2 / custom runtime)
- [ ] asynchronous perception-policy-action loop
- [ ] safety constraints and action guards
- [ ] continuous integration for regression and policy checks
