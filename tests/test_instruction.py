from generalist_vla_agent.agent.instruction import InstructionParser


def test_instruction_parser_intent_pick_and_place() -> None:
    parser = InstructionParser()
    parsed = parser.parse("Pick the block and place it into the bin.")
    assert parsed.intent == "pick_and_place"
    assert parsed.raw_text.startswith("Pick")
