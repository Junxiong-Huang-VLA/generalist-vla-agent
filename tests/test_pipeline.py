from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.utils.types import Observation


def test_mvp_pipeline_step_returns_action_payload() -> None:
    agent = GeneralistVLAAgent.from_defaults()
    obs = Observation(rgb=[0.2, 0.3, 0.9], depth=[0.5, 0.6], text="table scene")
    result = agent.step("Pick up the red cup.", obs)

    assert result["status"] == "ok"
    assert "action_name" in result
    assert "confidence" in result
    assert isinstance(result["params"], dict)
