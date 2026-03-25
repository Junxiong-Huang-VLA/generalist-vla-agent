import pytest

from generalist_vla_agent.data.schema import DatasetSchema, validate_rows


def test_validate_intent_rows_passes() -> None:
    rows = [
        {
            "instruction": "Move to marker",
            "intent": "navigate_or_move",
            "observation": {"rgb": [0.1], "depth": [0.2], "text": "scene"},
            "target_action": "navigate_to_waypoint",
        }
    ]
    validate_rows(rows, DatasetSchema(mode="intent"))


def test_validate_temporal_requires_prev_action() -> None:
    rows = [
        {
            "instruction": "Move to marker",
            "intent": "navigate_or_move",
            "observation": {"rgb": [0.1], "depth": [0.2], "text": "scene"},
            "target_action": "navigate_to_waypoint",
        }
    ]
    with pytest.raises(ValueError):
        validate_rows(rows, DatasetSchema(mode="temporal"))
