from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.utils.types import Observation


def test_openvla_mock_backend_is_runnable() -> None:
    cfg = {
        "policy": {
            "backend": "openvla_adapter",
            "backend_kwargs": {
                "dry_run_mock": True,
                "device": "cpu",
            },
        }
    }
    agent = GeneralistVLAAgent.from_config(cfg)
    obs = Observation(rgb=[0.2, 0.3, 0.4], depth=[0.8, 0.6], text="scene")
    result = agent.step("Move to the blue marker near the wall.", obs)
    assert result["status"] == "ok"
    assert result["params"]["backend"] == "openvla_adapter_mock"
