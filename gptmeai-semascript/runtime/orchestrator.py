"""System orchestrator for one deterministic loop cycle."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from core.event_store import EventStore
from core.execution_boundary import ExecutionBoundary
from core.governance import GovernanceEngine
from core.risk_engine import RiskEngine
from core.state_engine import StateEngine
from core.validation_engine import ValidationEngine


class Orchestrator:
    """Wire event store, replay, risk, governance, validation, and boundary."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.state_engine = StateEngine()
        self.risk_engine = RiskEngine()
        self.governance_engine = GovernanceEngine()
        self.validation_engine = ValidationEngine()
        self.execution_boundary = ExecutionBoundary()

    def run_cycle(self, cycle_number: int, proposal: Mapping[str, Any] | None = None) -> dict[str, Any]:
        event_log = self.event_store.get_all()
        state = self.state_engine.rebuild(event_log)
        snapshot = self._snapshot(state)
        mental_model = self._mental_model(snapshot)
        proposal = dict(proposal or self._generate_proposal(cycle_number, mental_model))
        risk = self.risk_engine.classify(proposal)
        governance = self.governance_engine.evaluate(proposal, state, risk)
        validation = self.validation_engine.validate_loop_integrity(
            event_log, state, proposal, risk, governance
        )
        approved = self._approval_rules(risk, governance, validation)
        boundary = self.execution_boundary.execute_if_approved(
            proposal, risk, governance, validation, approved
        )
        appended_event = None
        if boundary.get("event"):
            appended_event = self.event_store.append(boundary["event"])

        return {
            "cycle": cycle_number,
            "snapshot_id": snapshot["snapshot_id"],
            "mental_model_id": mental_model["mental_model_id"],
            "proposal_id": proposal["proposal_id"],
            "risk": risk,
            "governance": governance,
            "validation": validation,
            "approved": approved,
            "boundary_status": boundary["status"],
            "appended_event_id": appended_event["event_id"] if appended_event else None,
        }

    def _generate_proposal(self, cycle_number: int, mental_model: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "proposal_id": f"proposal::{cycle_number:03d}",
            "artifact_type": "implementation_root_skeleton",
            "mental_model_id": mental_model["mental_model_id"],
            "actions": [{"operation": "document", "target": "artifacts"}],
        }

    def _approval_rules(
        self,
        risk: Mapping[str, Any],
        governance: Mapping[str, Any],
        validation: Mapping[str, Any],
    ) -> bool:
        return (
            risk.get("risk_level") in {"LOW", "MEDIUM"}
            and governance.get("status") != "BLOCKED"
            and validation.get("valid") is True
        )

    def _snapshot(self, state: Mapping[str, Any]) -> dict[str, Any]:
        state_hash = self._hash(state)
        return {
            "snapshot_id": f"snapshot::{state_hash[-12:]}",
            "state_hash": state_hash,
            "state": dict(state),
            "projection_only": True,
        }

    def _mental_model(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        payload = {
            "snapshot_id": snapshot["snapshot_id"],
            "artifact_count": len(snapshot["state"].get("artifacts", {})),
            "proposal_count": len(snapshot["state"].get("proposals", {})),
            "canonical": snapshot["state"].get("canonical", {}),
        }
        return {
            "mental_model_id": f"mental::{self._hash(payload)[-12:]}",
            "derived_from_snapshot": snapshot["snapshot_id"],
            "decision_context": payload,
        }

    def _hash(self, value: Mapping[str, Any]) -> str:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
