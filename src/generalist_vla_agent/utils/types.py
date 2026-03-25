from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Instruction:
    raw_text: str
    intent: str
    entities: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Observation:
    rgb: list[float]
    depth: list[float]
    text: str = ""


@dataclass(slots=True)
class EncodedObservation:
    feature_vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ActionCommand:
    name: str
    confidence: float
    params: dict[str, Any] = field(default_factory=dict)
