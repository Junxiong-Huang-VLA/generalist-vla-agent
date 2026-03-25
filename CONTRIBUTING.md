# Contributing

Thanks for contributing to `generalist-vla-agent`.

## Quick Workflow

1. Create a branch from `main`.
2. Make focused changes with tests.
3. Run:
   - `python -m pytest -q -p no:cacheprovider`
   - `python scripts/run_demo_release.py --config configs/demo_release_small.yaml`
4. Open a PR with:
   - summary
   - validation commands
   - any config or metric impact

## Guidelines

- Keep module boundaries stable (`agent`, `policy`, `actions`, `eval`, `data`).
- Add new backends via adapter classes and config switches.
- Prefer deterministic configs and seed-aware behavior.
- If you change eval logic, update docs and benchmark outputs.

## Commit Style

Use concise prefixes:

- `feat:` new capability
- `fix:` bug fix
- `refactor:` internal cleanup
- `docs:` documentation only
- `test:` test changes
