from generalist_vla_agent.actions.postprocess import RuleBasedActionCalibrator
from generalist_vla_agent.utils.types import ActionCommand, Instruction


def test_rule_based_calibrator_fixes_gripper_close_case() -> None:
    calibrator = RuleBasedActionCalibrator(enable_gripper_close_fix=True)
    action = ActionCommand(name="hold_position", confidence=0.6, params={})
    instruction = Instruction(raw_text="close gripper", intent="manipulate", entities=["close"])
    out = calibrator.apply(action, instruction, context={"prev_action": "gripper_open"})
    assert out.name == "gripper_close"
