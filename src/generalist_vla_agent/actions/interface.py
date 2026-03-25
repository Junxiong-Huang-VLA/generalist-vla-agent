from __future__ import annotations

from abc import ABC, abstractmethod

from generalist_vla_agent.utils.types import ActionCommand


class ActionInterface(ABC):
    """Abstract action bridge for simulator or real robot backends."""

    @abstractmethod
    def execute(self, action: ActionCommand) -> dict:
        raise NotImplementedError


class DryRunActionInterface(ActionInterface):
    """Non-destructive action backend for development and CI."""

    def execute(self, action: ActionCommand) -> dict:
        return {
            "status": "ok",
            "action_name": action.name,
            "confidence": action.confidence,
            "params": action.params,
        }
