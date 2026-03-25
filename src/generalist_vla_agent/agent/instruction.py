from __future__ import annotations

from typing import Any

from generalist_vla_agent.utils.types import Instruction


class InstructionParser:
    """Simple parser for MVP; replace with LLM/VLM parser in later iterations."""

    KEYWORD_INTENT_MAP = {
        "pick": "pick_and_place",
        "place": "pick_and_place",
        "move": "navigate_or_move",
        "push": "manipulate",
    }

    def parse(self, text: str, context: dict[str, Any] | None = None) -> Instruction:
        clean = (text or "").strip()
        lowered = clean.lower()
        context = context or {}

        intent = "generic_task"
        for keyword, mapped_intent in self.KEYWORD_INTENT_MAP.items():
            if keyword in lowered:
                intent = mapped_intent
                break

        hint = context.get("intent_hint")
        hint_mode = str(context.get("intent_hint_mode", "off")).strip().lower()
        if hint and hint_mode == "strict":
            intent = str(hint)
        elif hint and hint_mode == "weak" and intent == "generic_task":
            intent = str(hint)

        entities = [token.strip(".,!?") for token in clean.split() if len(token) > 2]
        return Instruction(
            raw_text=clean,
            intent=intent,
            entities=entities[:6],
            context=context,
        )
