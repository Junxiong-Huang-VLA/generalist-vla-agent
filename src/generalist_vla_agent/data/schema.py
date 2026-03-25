from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatasetSchema:
    version: str = "v1"
    mode: str = "intent"

    def validate_mode(self) -> None:
        if self.mode not in {"intent", "temporal"}:
            raise ValueError(f"Unsupported dataset schema mode: {self.mode}")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_row(row: dict[str, Any], schema: DatasetSchema) -> None:
    schema.validate_mode()
    required = {"instruction", "intent", "observation", "target_action"}
    missing = required - set(row.keys())
    _assert(not missing, f"Missing required fields: {sorted(missing)}")

    _assert(isinstance(row["instruction"], str) and row["instruction"], "instruction must be non-empty str")
    _assert(isinstance(row["intent"], str) and row["intent"], "intent must be non-empty str")
    _assert(
        isinstance(row["target_action"], str) and row["target_action"],
        "target_action must be non-empty str",
    )

    obs = row["observation"]
    _assert(isinstance(obs, dict), "observation must be dict")
    _assert("rgb" in obs and "depth" in obs, "observation must include rgb/depth")
    _assert(isinstance(obs["rgb"], list) and len(obs["rgb"]) > 0, "observation.rgb must be non-empty list")
    _assert(
        isinstance(obs["depth"], list) and len(obs["depth"]) > 0,
        "observation.depth must be non-empty list",
    )
    for value in obs["rgb"] + obs["depth"]:
        _assert(isinstance(value, (int, float)), "observation rgb/depth values must be numeric")

    if schema.mode == "temporal":
        _assert("prev_action" in row, "temporal row missing prev_action")
        _assert(isinstance(row["prev_action"], str), "prev_action must be str")
        if "sequence_id" in row:
            _assert(isinstance(row["sequence_id"], str) and row["sequence_id"], "sequence_id must be non-empty str")


def validate_rows(rows: list[dict[str, Any]], schema: DatasetSchema) -> None:
    _assert(len(rows) > 0, "dataset cannot be empty")
    for idx, row in enumerate(rows):
        try:
            validate_row(row, schema)
        except ValueError as exc:
            raise ValueError(f"row[{idx}] invalid: {exc}") from exc
