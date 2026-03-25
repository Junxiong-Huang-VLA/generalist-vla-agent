from __future__ import annotations

from pathlib import Path
from typing import Any

from generalist_vla_agent.utils.config import load_yaml_config


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config_with_extends(config_path: str) -> dict[str, Any]:
    def _load_recursive(path: Path, visited: set[Path]) -> dict[str, Any]:
        resolved = path.resolve()
        if resolved in visited:
            raise ValueError(f"Cyclic config extends detected: {resolved}")
        visited.add(resolved)

        cfg = load_yaml_config(path)
        extends = cfg.pop("extends", None)
        if not extends:
            return cfg

        base_path = path.parent / extends
        base_cfg = _load_recursive(base_path, visited)
        return _deep_merge(base_cfg, cfg)

    return _load_recursive(Path(config_path), set())
