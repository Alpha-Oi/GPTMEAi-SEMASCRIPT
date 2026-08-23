"""Final execution boundary."""

from __future__ import annotations

from typing import Any, Mapping


class ExecutionBoundary:
    """Final deterministic execution gate.

    The bootstrap implementation records approved actions. It does not perform
    external side effects or mutate state directly.
    """

    def execute_if_approved(
        self,
        proposal: Mapping[str, Any],
        risk_result: Mapping[str, Any],
        governance_decision: Mapping[str, Any],
        validation_result: Mapping[str, Any],
        approved: bool,
    ) -> dict[str, Any]:
        if risk_result.get("risk_level") in {"BLOCKED", "HIGH"}:
            return self._rejected(proposal, "risk blocked execution")
        if governance_decision.get("status") == "BLOCKED":
            return self._rejected(proposal, "governance blocked execution")
        if validation_result.get("valid") is not True:
            return self._rejected(proposal, "validation failed")
        if approved is not True:
            return self._rejected(proposal, "approval missing")

        proposal_id = str(proposal.get("proposal_id", "proposal::unknown"))
        event = {
            "event_id": f"event::{proposal_id}::approved-action",
            "event_type": "APPROVED_ACTION_RECORDED",
            "artifact_id": proposal_id,
            "payload": {
                "proposal_id": proposal_id,
                "actions": list(proposal.get("actions", [])),
                "governance": dict(governance_decision),
            },
        }
        return {"status": "APPROVED_RECORDED", "event": event, "executed": False}

    def _rejected(self, proposal: Mapping[str, Any], reason: str) -> dict[str, Any]:
        proposal_id = str(proposal.get("proposal_id", "proposal::unknown"))
        return {
            "status": "REJECTED",
            "event": {
                "event_id": f"event::{proposal_id}::execution-rejected",
                "event_type": "EXECUTION_REJECTED",
                "artifact_id": proposal_id,
                "payload": {"proposal_id": proposal_id, "reason": reason},
            },
            "executed": False,
        }
