"""Closed-loop validation engine."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .governance import GovernanceEngine
from .risk_engine import RiskEngine
from .state_engine import StateEngine


class ValidationEngine:
    """Validate replay, risk, governance, and loop consistency."""

    def __init__(self):
        self.state_engine = StateEngine()
        self.risk_engine = RiskEngine()
        self.governance_engine = GovernanceEngine()

    def validate_loop_integrity(
        self,
        event_log: Iterable[Mapping[str, Any]],
        state: Mapping[str, Any],
        proposal: Mapping[str, Any],
        risk_result: Mapping[str, Any],
        governance_decision: Mapping[str, Any],
    ) -> dict[str, Any]:
        replay_ok = self.verify_consistency(event_log, state)["consistent"]
        risk_ok = self.risk_engine.classify(proposal) == dict(risk_result)
        governance_ok = self.governance_engine.evaluate(proposal, state, risk_result) == dict(
            governance_decision
        )
        no_bypass = not (
            risk_result.get("risk_level") == "BLOCKED"
            and governance_decision.get("status") != "BLOCKED"
        )
        return {
            "valid": replay_ok and risk_ok and governance_ok and no_bypass,
            "event_replay_consistency": replay_ok,
            "risk_determinism": risk_ok,
            "governance_determinism": governance_ok,
            "no_bypass_paths": no_bypass,
        }

    def check_drift(
        self,
        event_log: Iterable[Mapping[str, Any]],
        observed_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        rebuilt = self.state_engine.rebuild(event_log)
        return {
            "drift_detected": rebuilt != dict(observed_state),
            "expected_state": rebuilt,
            "observed_state": dict(observed_state),
        }

    def verify_consistency(
        self,
        event_log: Iterable[Mapping[str, Any]],
        state: Mapping[str, Any],
    ) -> dict[str, Any]:
        rebuilt = self.state_engine.rebuild(event_log)
        return {"consistent": rebuilt == dict(state), "rebuilt_state": rebuilt}
