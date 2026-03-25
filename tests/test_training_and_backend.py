from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.data.synthetic import generate_synthetic_dataset
from generalist_vla_agent.training.trainer import train_intent_policy
from generalist_vla_agent.utils.types import Observation


def test_trained_intent_backend_predicts_expected_action() -> None:
    rows = generate_synthetic_dataset(num_samples=24, seed=123)
    artifact_path = "outputs/test_models/intent_policy_test.json"
    train_intent_policy(samples=rows, artifact_path=artifact_path)

    cfg = {
        "policy": {
            "backend": "trained_intent",
            "backend_kwargs": {"artifact_path": artifact_path},
        }
    }
    agent = GeneralistVLAAgent.from_config(cfg)
    obs = Observation(rgb=[0.5, 0.3, 0.2], depth=[0.8, 0.4, 0.2], text="scene")
    result = agent.step("Move to the blue marker near the wall.", obs)
    assert result["action_name"] == "navigate_to_waypoint"
