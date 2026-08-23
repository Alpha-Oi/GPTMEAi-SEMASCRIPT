"""Deterministic governed enforcement for drift response events."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


RESPONSE_TO_ACTION = {
    "BLOCK_EXECUTION": "BLOCK_EXECUTION",
    "ROLLBACK": "ROLLBACK_STATE",
    "STAGE_FIX": "APPLY_FIX",
    "REVALIDATE": "REVALIDATE_SYSTEM",
    "NO_ACTION": "NO_ACTION",
}


class ExecutionEnforcementEngine:
    """Final control layer for approved governed actions.

    The engine does not perform external execution, does not mutate runtime
    files, and does not append to an event store by itself. It returns an
    auditable action result plus an `EXECUTION_ENFORCED` event object.
    """

    def __init__(self):
        self._drift_response_event: dict[str, Any] = {}
        self._governance_approval: dict[str, Any] = {}
        self._risk_result: dict[str, Any] = {}
        self._action_type = "NO_ACTION"
        self._gate: dict[str, Any] = {}
        self._last_result: dict[str, Any] = {}

    def evaluate_response(
        self,
        drift_response: Mapping[str, Any],
        governance_approval: Mapping[str, Any] | None = None,
        risk_result: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate a drift response event under governance and risk gates."""
        self._drift_response_event = deepcopy(dict(drift_response))
        self._governance_approval = deepcopy(dict(governance_approval or {}))
        self._risk_result = deepcopy(dict(risk_result or {}))
        self._action_type = self._action_type_from_response()
        self._gate = self.check_governance()
        result = self.apply_action()
        result["event"] = self.emit_event(result)
        result["event_emitted"] = True
        self._last_result = deepcopy(result)
        return result

    def check_governance(self) -> dict[str, Any]:
        """Return deterministic gate decision for the current response."""
        response_type = self._response_type()
        risk_level = self._risk_level()
        approved = self._governance_approval.get("approved") is True

        if response_type == "BLOCK_EXECUTION":
            return {
                "execution_status": "BLOCKED",
                "reason": "BLOCK_EXECUTION response has highest priority",
            }
        if self._action_type != "NO_ACTION" and risk_level in {"BLOCKED", "HIGH"}:
            return {
                "execution_status": "BLOCKED",
                "reason": f"risk level {risk_level} blocks enforcement",
            }
        if response_type in {"ROLLBACK", "STAGE_FIX"} and not approved:
            return {
                "execution_status": "REJECTED",
                "reason": f"{response_type} requires governance approval",
            }
        return {
            "execution_status": "APPROVED",
            "reason": "governance and risk gates satisfied",
        }

    def apply_action(self) -> dict[str, Any]:
        """Apply an audit-only enforcement decision."""
        status = self._gate["execution_status"]
        applied_changes = []
        if status == "APPROVED":
            applied_changes = [f"AUDIT_ONLY: {self._action_type}"]

        return {
            "action_type": self._action_type,
            "execution_status": status,
            "applied_changes": applied_changes,
            "event_emitted": False,
            "source_response_id": self._source_response_id(),
            "governance_decision": self._governance_decision(),
            "risk_level": self._risk_level(),
            "gate_reason": self._gate["reason"],
            "runtime_mutation": False,
            "external_execution": False,
        }

    def emit_event(self, action_result: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return an EXECUTION_ENFORCED event object without appending it."""
        result = dict(action_result or self._last_result)
        source_response_id = str(result.get("source_response_id", self._source_response_id()))
        action_type = str(result.get("action_type", self._action_type))
        status = str(result.get("execution_status", "REJECTED"))
        return {
            "event_id": f"event::execution-enforced::{source_response_id}::{action_type.lower()}::{status.lower()}",
            "event_type": "EXECUTION_ENFORCED",
            "artifact_id": "governed-execution-enforcement-layer::1.0",
            "payload": {
                "action_type": action_type,
                "source_response_id": source_response_id,
                "governance_decision": result.get("governance_decision", self._governance_decision()),
                "risk_level": result.get("risk_level", self._risk_level()),
                "applied_changes": list(result.get("applied_changes", [])),
                "execution_status": status,
                "runtime_mutation": False,
                "external_execution": False,
            },
        }

    def governance_rules(self) -> list[str]:
        """Return hard rules enforced by this layer."""
        return [
            "MUST NOT execute unapproved actions",
            "MUST respect risk engine output",
            "MUST respect governance decisions",
            "MUST be deterministic",
            "MUST NEVER bypass event_store",
            "MUST NOT self-modify enforcement logic",
            "MUST NOT perform external execution",
            "MUST NOT perform uncontrolled runtime mutation",
        ]

    def _response_type(self) -> str:
        payload = dict(self._drift_response_event.get("payload", {}))
        return str(payload.get("response_type", "NO_ACTION"))

    def _action_type_from_response(self) -> str:
        return RESPONSE_TO_ACTION.get(self._response_type(), "NO_ACTION")

    def _source_response_id(self) -> str:
        return str(self._drift_response_event.get("event_id", "event::drift-response::unknown"))

    def _risk_level(self) -> str:
        return str(self._risk_result.get("risk_level", "LOW"))

    def _governance_decision(self) -> str:
        if self._governance_approval.get("approved") is True:
            return str(self._governance_approval.get("decision", "APPROVED"))
        if "decision" in self._governance_approval:
            return str(self._governance_approval["decision"])
        return "NOT_PROVIDED"
