from __future__ import annotations

import random


def generate_synthetic_dataset(num_samples: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    templates = [
        (
            "Pick up the red cup and place it on the tray.",
            "pick_and_place",
            "move_to_target",
        ),
        (
            "Move to the blue marker near the wall.",
            "navigate_or_move",
            "navigate_to_waypoint",
        ),
        (
            "Push the small box to the left side.",
            "manipulate",
            "apply_push",
        ),
        (
            "Scan the table for available tools.",
            "generic_task",
            "scan_scene",
        ),
    ]

    rows: list[dict] = []
    for idx in range(num_samples):
        instruction, intent, target_action = templates[idx % len(templates)]
        rgb = [round(rng.uniform(0.1, 1.0), 3) for _ in range(3)]
        depth = [round(rng.uniform(0.1, 1.0), 3) for _ in range(3)]
        rows.append(
            {
                "instruction": instruction,
                "intent": intent,
                "observation": {
                    "rgb": rgb,
                    "depth": depth,
                    "text": "synthetic tabletop scene",
                },
                "target_action": target_action,
            }
        )
    return rows


def generate_synthetic_temporal_dataset(num_samples: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)

    trajectories = {
        "pick_and_place": (
            "Pick up the red cup and place it on the tray.",
            ["search_target", "move_to_target", "grasp_object", "place_object"],
        ),
        "navigate_or_move": (
            "Move to the blue marker near the wall.",
            ["scan_scene", "navigate_to_waypoint", "align_pose"],
        ),
        "manipulate": (
            "Push the small box to the left side.",
            ["align_tool", "apply_push", "stabilize"],
        ),
        "generic_task": (
            "Scan the table for available tools.",
            ["scan_scene", "hold_position"],
        ),
    }

    rows: list[dict] = []
    seq_idx = 0
    intent_items = list(trajectories.items())
    while len(rows) < num_samples:
        intent, (instruction, actions) = intent_items[seq_idx % len(intent_items)]
        sequence_id = f"synthetic_seq_{seq_idx:06d}"
        prev_action = "<none>"

        for step_idx, target_action in enumerate(actions):
            if len(rows) >= num_samples:
                break
            rgb = [round(rng.uniform(0.1, 1.0), 3) for _ in range(3)]
            depth = [round(rng.uniform(0.1, 1.0), 3) for _ in range(3)]
            rows.append(
                {
                    "sequence_id": sequence_id,
                    "instruction": instruction,
                    "intent": intent,
                    "prev_action": prev_action,
                    "step_index": step_idx,
                    "observation": {
                        "rgb": rgb,
                        "depth": depth,
                        "text": "synthetic temporal tabletop scene",
                    },
                    "target_action": target_action,
                }
            )
            prev_action = target_action
        seq_idx += 1
    return rows
