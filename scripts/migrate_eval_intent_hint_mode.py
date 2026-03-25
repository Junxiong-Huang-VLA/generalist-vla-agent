from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add default intent_hint_mode to eval config files.")
    parser.add_argument("--configs-dir", default="configs")
    parser.add_argument("--default-mode", default="weak", choices=["off", "weak", "strict"])
    parser.add_argument("--apply", action="store_true", help="Write changes to files.")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid yaml mapping: {path}")
    return data


def main() -> None:
    args = parse_args()
    configs_dir = Path(args.configs_dir)
    targets = sorted(configs_dir.glob("*eval*.yaml"))

    changed: list[Path] = []
    for path in targets:
        data = _load_yaml(path)
        eval_cfg = data.get("eval")
        if not isinstance(eval_cfg, dict):
            continue
        if "intent_hint_mode" in eval_cfg:
            continue
        eval_cfg["intent_hint_mode"] = args.default_mode
        changed.append(path)
        if args.apply:
            with path.open("w", encoding="utf-8") as fp:
                yaml.safe_dump(data, fp, sort_keys=False, allow_unicode=False)

    mode = "APPLY" if args.apply else "DRY_RUN"
    print(f"mode={mode} default_mode={args.default_mode} changed={len(changed)}")
    for p in changed:
        print(p.as_posix())


if __name__ == "__main__":
    main()
