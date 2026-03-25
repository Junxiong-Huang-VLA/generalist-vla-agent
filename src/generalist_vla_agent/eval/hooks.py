from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from generalist_vla_agent.utils.types import ActionCommand

EvalHook = Callable[[ActionCommand, dict], None]


@dataclass
class EvalHookManager:
    hooks: list[EvalHook] = field(default_factory=list)

    def register(self, hook: EvalHook) -> None:
        self.hooks.append(hook)

    def run(self, action: ActionCommand, execution_result: dict) -> None:
        for hook in self.hooks:
            hook(action, execution_result)


def success_rate_hook(action: ActionCommand, execution_result: dict) -> None:
    _ = action
    _ = execution_result
    # Placeholder for metric accumulation backend.
