"""Integrated closed evolution loop wiring."""

from __future__ import annotations

from typing import Any, Mapping

from cognition import CognitiveInterpreter
from event_store import EventStore, EventValidator, EventWriter
from governance import GovernanceEngine
from risk import BlockerEngine, RiskClassifier
from snapshot import SnapshotGenerator
from system_runtime import RuntimeController
from validation import LoopValidator


class ClosedEvolutionLoop:
    """Deterministic event-sourced control loop.

    Flow:
    event_log -> reconstruction/snapshot -> mental model -> risk -> validation
    -> governance -> approval -> dry-run runtime boundary -> event_log append.
    """

    def __init__(
        self,
        event_store: EventStore | None = None,
        risk_classifier: RiskClassifier | None = None,
        governance_engine: GovernanceEngine | None = None,
        runtime_controller: RuntimeController | None = None,
    ):
        self.event_store = event_store or EventStore()
        self.event_writer = EventWriter(self.event_store, EventValidator())
        self.snapshot_generator = SnapshotGenerator()
        self.interpreter = CognitiveInterpreter()
        self.loop_validator = LoopValidator(self.snapshot_generator)
        self.risk_classifier = risk_classifier or RiskClassifier()
        self.blocker_engine = BlockerEngine()
        self.governance_engine = governance_engine or GovernanceEngine()
        self.runtime_controller = runtime_controller or RuntimeController()

    def run(self, proposal: Mapping[str, Any], approval: Mapping[str, Any] | None = None) -> dict[str, Any]:
        approval = dict(approval or {})
        events_before = self.event_store.read_all()
        snapshot = self.snapshot_generator.generate(events_before)
        mental_model = self.interpreter.interpret(snapshot)
        validation = self.loop_validator.validate(events_before, snapshot)
        risk = self.risk_classifier.classify(proposal)

        if self.blocker_engine.is_blocked(risk):
            return {
                "status": "BLOCKED",
                "snapshot": snapshot,
                "mental_model": mental_model,
                "validation": validation,
                "risk": risk,
                "runtime": {"dry_run": True, "executed": False},
            }

        if not validation["valid"]:
            return {
                "status": "VALIDATION_FAILED",
                "snapshot": snapshot,
                "mental_model": mental_model,
                "validation": validation,
                "risk": risk,
                "runtime": {"dry_run": True, "executed": False},
            }

        if approval.get("approved") is not True:
            return {
                "status": "WAITING_FOR_APPROVAL",
                "snapshot": snapshot,
                "mental_model": mental_model,
                "validation": validation,
                "risk": risk,
                "runtime": {"dry_run": True, "executed": False},
            }

        event = self._approval_event(proposal)
        stored_event = self.event_writer.append(event)
        runtime = self.runtime_controller.run(stored_event, risk, approval)
        return {
            "status": "COMPLETED",
            "snapshot": snapshot,
            "mental_model": mental_model,
            "validation": validation,
            "risk": risk,
            "runtime": runtime,
        }

    def _approval_event(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        proposal_id = str(proposal.get("proposal_id", "proposal::unknown"))
        sequence = len(self.event_store) + 1
        return {
            "event_id": f"event::{proposal_id}::approved::{sequence:06d}",
            "event_type": "APPROVED_ACTION_RECORDED",
            "artifact_id": proposal_id,
            "new_state": "APPROVED",
            "payload": {
                "proposal_id": proposal_id,
                "artifact_type": proposal.get("artifact_type", ""),
                "actions": list(proposal.get("actions", [])),
            },
        }
