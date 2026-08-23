"""Runtime controller enforcing governance and risk boundaries."""

from __future__ import annotations

from typing import Any, Mapping

from .action_dispatcher import ActionDispatcher


class RuntimeController:
    """Controller that never bypasses risk or approval gates."""

    def __init__(self, dispatcher: ActionDispatcher | None = None):
        self.dispatcher = dispatcher or ActionDispatcher()

    def run(
        self,
        approved_event: Mapping[str, Any],
        risk_result: Mapping[str, Any],
        approval: Mapping[str, Any],
    ) -> dict[str, Any]:
        return self.dispatcher.dispatch(approved_event, risk_result, approval)
