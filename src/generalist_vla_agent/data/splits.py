from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SplitSpec:
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1

    def validate(self) -> None:
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Split ratios must sum to 1.0, got {total:.6f}")
        if min(self.train_ratio, self.val_ratio, self.test_ratio) < 0:
            raise ValueError("Split ratios must be non-negative")


def split_rows(
    rows: list[dict[str, Any]],
    spec: SplitSpec | None = None,
    seed: int = 42,
) -> dict[str, list[dict[str, Any]]]:
    spec = spec or SplitSpec()
    spec.validate()

    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    n = len(shuffled)

    n_train = int(n * spec.train_ratio)
    n_val = int(n * spec.val_ratio)
    n_test = n - n_train - n_val

    train_rows = shuffled[:n_train]
    val_rows = shuffled[n_train : n_train + n_val]
    test_rows = shuffled[n_train + n_val : n_train + n_val + n_test]

    return {"train": train_rows, "val": val_rows, "test": test_rows}
