"""Governed response policy for detected drift."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class DriftResponseEngine:
    """Evaluate drift reports and stage governed correction proposals.

    The engine never applies fixes, never mutates runtime state, and never
    bypasses risk or governance. It only returns deterministic response objects.
    """

    def __init__(self):
        self._last_drift_report: dict[str, Any] = {}
        self._last_response_type = "NO_ACTION"

    def evaluate_drift(self, drift_report: Mapping[str, Any]) -> dict[str, Any]:
        """Evaluate a drift report and return a governed response."""
        self._last_drift_report = deepcopy(dict(drift_report))
        response_type = self.classify_response()
        self._last_response_type = response_type
        return self.generate_governed_action()

    def classify_response(self) -> str:
        """Classify the deterministic response type from drift severity."""
        report = self._last_drift_report
        drift_status = report.get("drift_status", "NO_DRIFT")
        drift_level = report.get("drift_level", "LOW")
        drift_types = set(report.get("drift_types", []))

        if drift_status == "NO_DRIFT" or not drift_types:
            return "NO_ACTION"
        if drift_level == "CRITICAL":
            return "BLOCK_EXECUTION"
        if drift_level == "HIGH":
            if drift_types & {"EVENT_DRIFT", "GOVERNANCE_DRIFT"}:
                return "ROLLBACK"
            return "STAGE_FIX"
        if drift_level == "MEDIUM":
            if drift_types & {"STRUCTURAL_DRIFT", "GOVERNANCE_DRIFT", "EVENT_DRIFT"}:
                return "STAGE_FIX"
            return "REVALIDATE"
        return "REVALIDATE"

    def generate_governed_action(self) -> dict[str, Any]:
        """Generate a response object and optional staged proposal."""
        report = self._last_drift_report
        response_type = self._last_response_type
        affected_layers = sorted(report.get("affected_layers", []))
        drift_types = sorted(report.get("drift_types", []))
        severity = str(report.get("drift_level", "LOW"))
        proposal = self._proposal_for_response(response_type, report, drift_types, affected_layers)

        return {
            "response_type": response_type,
            "severity_assessment": self._severity_assessment(response_type, severity, drift_types),
            "affected_layers": affected_layers,
            "recommended_action": self._recommended_action(response_type, severity),
            "requires_governance_approval": response_type in {
                "BLOCK_EXECUTION",
                "STAGE_FIX",
                "ROLLBACK",
            },
            "staged_proposal": proposal,
            "governance_rules": self.governance_rules(),
        }

    def emit_response_event(
        self,
        response: Mapping[str, Any],
        drift_report_id: str = "drift-report::unknown",
    ) -> dict[str, Any]:
        """Return a DRIFT_RESPONSE_GENERATED event without appending it."""
        response_type = str(response.get("response_type", "NO_ACTION"))
        return {
            "event_id": f"event::drift-response::{drift_report_id}::{response_type.lower()}",
            "event_type": "DRIFT_RESPONSE_GENERATED",
            "artifact_id": "drift-response-layer::1.0",
            "payload": {
                "drift_report_id": drift_report_id,
                "response_type": response_type,
                "reasoning": response.get("severity_assessment", ""),
                "staged_proposal": deepcopy(response.get("staged_proposal", {})),
            },
        }

    def governance_rules(self) -> list[str]:
        """Return the hard governance rules enforced by this layer."""
        return [
            "MUST NOT modify runtime system",
            "MUST NOT apply fixes automatically",
            "MUST NOT bypass risk engine",
            "MUST be deterministic",
            "MUST require governance approval for STAGE_FIX or ROLLBACK",
            "MUST treat BLOCK_EXECUTION as highest priority response",
            "MUST remain governance-controlled only",
        ]

    def _proposal_for_response(
        self,
        response_type: str,
        report: Mapping[str, Any],
        drift_types: list[str],
        affected_layers: list[str],
    ) -> dict[str, Any]:
        if response_type == "NO_ACTION":
            return {}

        action_by_response = {
            "BLOCK_EXECUTION": "block_execution",
            "STAGE_FIX": "stage_fix",
            "ROLLBACK": "stage_rollback",
            "REVALIDATE": "revalidate",
        }
        return {
            "proposal_id": f"drift-correction::{response_type.lower()}",
            "action": action_by_response[response_type],
            "source_drift_status": report.get("drift_status", "NO_DRIFT"),
            "drift_level": report.get("drift_level", "LOW"),
            "drift_types": drift_types,
            "affected_layers": affected_layers,
            "requires_risk_review": True,
            "requires_governance_approval": response_type in {
                "BLOCK_EXECUTION",
                "STAGE_FIX",
                "ROLLBACK",
            },
            "auto_apply": False,
            "runtime_mutation": False,
        }

    def _severity_assessment(self, response_type: str, severity: str, drift_types: list[str]) -> str:
        joined = ", ".join(drift_types) if drift_types else "none"
        return (
            f"{severity} drift mapped to {response_type}; "
            f"detected drift types: {joined}; no automatic correction is allowed."
        )

    def _recommended_action(self, response_type: str, severity: str) -> str:
        if response_type == "NO_ACTION":
            return "No correction proposal required."
        if response_type == "BLOCK_EXECUTION":
            return "Stage execution block proposal and require governance review."
        if response_type == "ROLLBACK":
            return "Stage rollback proposal for governance review; do not apply automatically."
        if response_type == "STAGE_FIX":
            return "Stage bounded correction proposal for governance and risk review."
        return "Revalidate artifact/runtime consistency before staging a fix."
