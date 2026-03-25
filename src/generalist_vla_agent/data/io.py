from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    src = Path(path)
    rows: list[dict[str, Any]] = []
    with src.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows
