from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    return data
