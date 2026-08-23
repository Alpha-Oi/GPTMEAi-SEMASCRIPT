"""Governance engine."""

from __future__ import annotations

from typing import Any, Mapping


class GovernanceEngine:
    """Evaluate proposals and select canonical artifacts without bypassing risk."""

    TRUST_ORDER = {"high": 3, "medium": 2, "low": 1, "unknown": 0}

    def evaluate(
        self,
        proposal: Mapping[str, Any],
        state: Mapping[str, Any],
        risk_result: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return deterministic governance decision."""
        if risk_result.get("risk_level") == "BLOCKED":
            return {
                "proposal_id": proposal.get("proposal_id", ""),
                "status": "BLOCKED",
                "canonical_artifact_id": None,
                "reason": "risk engine blocked proposal",
            }

        artifact_type = str(proposal.get("artifact_type", "implementation_root_skeleton"))
        canonical = self.select_canonical(artifact_type, state)
        return {
            "proposal_id": proposal.get("proposal_id", ""),
            "status": "APPROVABLE",
            "artifact_type": artifact_type,
            "canonical_artifact_id": canonical,
            "reason": "deterministic governance evaluation",
        }

    def select_canonical(self, artifact_type: str, state: Mapping[str, Any]) -> str | None:
        """Select canonical artifact by active state, trust, and ID."""
        artifacts = dict(state.get("artifacts", {}))
        candidates = [
            dict(artifact)
            for artifact in artifacts.values()
            if artifact.get("type") == artifact_type and artifact.get("state") == "ACTIVE"
        ]
        if not candidates:
            return None
        ranked = sorted(
            candidates,
            key=lambda item: (
                self.TRUST_ORDER.get(str(item.get("trust", "unknown")), 0),
                str(item.get("artifact_id", "")),
            ),
            reverse=True,
        )
        return str(ranked[0]["artifact_id"])

    def emit_decision_event(self, decision: Mapping[str, Any]) -> dict[str, Any]:
        """Create a deterministic governance decision event."""
        proposal_id = str(decision.get("proposal_id", "proposal::unknown"))
        return {
            "event_id": f"event::{proposal_id}::governance-decision",
            "event_type": "GOVERNANCE_DECISION",
            "artifact_id": proposal_id,
            "payload": dict(decision),
        }
