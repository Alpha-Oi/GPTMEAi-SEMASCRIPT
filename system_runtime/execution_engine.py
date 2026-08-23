"""Execution engine boundary."""

from __future__ import annotations

from typing import Any, Mapping


class ExecutionEngine:
    """Dry-run execution boundary.

    The skeleton never performs real runtime side effects. It only confirms
    whether a request would be allowed after risk, validation, and approval.
    """

    def execute(
        self,
        approved_event: Mapping[str, Any],
        risk_result: Mapping[str, Any],
        approval: Mapping[str, Any],
    ) -> dict[str, Any]:
        if risk_result.get("risk_level") == "BLOCKED":
            return {"status": "BLOCKED", "dry_run": True, "executed": False}
        if approval.get("approved") is not True:
            return {"status": "WAITING_FOR_APPROVAL", "dry_run": True, "executed": False}
        return {
            "status": "DRY_RUN_ACCEPTED",
            "dry_run": True,
            "executed": False,
            "event_id": approved_event.get("event_id"),
        }
