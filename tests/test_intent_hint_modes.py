from generalist_vla_agent.agent.instruction import InstructionParser


def test_intent_hint_modes() -> None:
    parser = InstructionParser()
    text = "sweep the block to the right"

    off = parser.parse(text, context={"intent_hint": "navigate_or_move", "intent_hint_mode": "off"})
    weak = parser.parse(text, context={"intent_hint": "navigate_or_move", "intent_hint_mode": "weak"})
    strict = parser.parse(text, context={"intent_hint": "navigate_or_move", "intent_hint_mode": "strict"})

    assert off.intent == "generic_task"
    assert weak.intent == "navigate_or_move"
    assert strict.intent == "navigate_or_move"
