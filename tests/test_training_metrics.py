from generalist_vla_agent.training.trainer import evaluate_artifact_accuracy


def test_evaluate_artifact_accuracy_temporal() -> None:
    artifact = {
        "intent_prev_to_action": {"pick_and_place|move_to_target": "grasp_object"},
        "intent_to_action": {"pick_and_place": "move_to_target"},
    }
    rows = [
        {
            "intent": "pick_and_place",
            "prev_action": "move_to_target",
            "target_action": "grasp_object",
        },
        {
            "intent": "pick_and_place",
            "prev_action": "<none>",
            "target_action": "move_to_target",
        },
    ]
    metrics = evaluate_artifact_accuracy(artifact=artifact, rows=rows, backend="trained_temporal")
    assert metrics["action_accuracy"] == 1.0
