"""Action dispatcher boundary."""

from __future__ import annotations

from typing import Any, Mapping

from .execution_engine import ExecutionEngine


class ActionDispatcher:
    """Dispatch approved actions to the dry-run execution boundary."""

    def __init__(self, execution_engine: ExecutionEngine | None = None):
        self.execution_engine = execution_engine or ExecutionEngine()

    def dispatch(
        self,
        approved_event: Mapping[str, Any],
        risk_result: Mapping[str, Any],
        approval: Mapping[str, Any],
    ) -> dict[str, Any]:
        return self.execution_engine.execute(approved_event, risk_result, approval)
