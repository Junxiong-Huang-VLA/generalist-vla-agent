from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.data.synthetic import generate_synthetic_temporal_dataset
from generalist_vla_agent.training.trainer import train_temporal_policy
from generalist_vla_agent.utils.types import Observation


def test_temporal_backend_respects_prev_action() -> None:
    rows = generate_synthetic_temporal_dataset(num_samples=60, seed=321)
    artifact_path = "outputs/test_models/temporal_policy_test.json"
    train_temporal_policy(samples=rows, artifact_path=artifact_path)

    cfg = {
        "policy": {
            "backend": "trained_temporal",
            "backend_kwargs": {"artifact_path": artifact_path},
        }
    }
    agent = GeneralistVLAAgent.from_config(cfg)
    obs = Observation(rgb=[0.4, 0.5, 0.7], depth=[0.8, 0.3, 0.2], text="scene")

    result = agent.step(
        "Pick up the red cup and place it on the tray.",
        obs,
        context={"prev_action": "move_to_target"},
    )
    assert result["action_name"] == "grasp_object"
