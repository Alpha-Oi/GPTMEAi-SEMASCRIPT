"""Deterministic risk classification engine."""

from __future__ import annotations

from typing import Any, Mapping


class RiskEngine:
    """Classify proposals before governance approval or execution."""

    BLOCKED_OPERATIONS = {
        "bypass_governance",
        "bypass_risk",
        "direct_runtime_mutation",
        "mutate_memory",
        "mutate_runtime",
        "mutate_storage",
    }
    HIGH_OPERATIONS = {"delete", "network", "shell", "write"}

    def classify(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        """Return a deterministic risk classification."""
        score_result = self.compute_score(proposal)
        score = score_result["score"]
        if score_result["blockers"]:
            risk_level = "BLOCKED"
        elif score >= 70:
            risk_level = "HIGH"
        elif score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        return {
            "proposal_id": proposal.get("proposal_id", ""),
            "risk_level": risk_level,
            "score": score,
            "blockers": score_result["blockers"],
        }

    def compute_score(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        """Compute deterministic score from operation names only."""
        score = 10
        blockers = []
        actions = proposal.get("actions", [])
        for action in actions if isinstance(actions, list) else []:
            operation = str(dict(action).get("operation", "")).strip().lower()
            if operation in self.BLOCKED_OPERATIONS:
                blockers.append({"operation": operation, "reason": "blocked operation"})
                score = 100
            elif operation in self.HIGH_OPERATIONS:
                score = max(score, 75)
        return {"score": score, "blockers": blockers}

    def block_if_needed(self, risk_result: Mapping[str, Any]) -> dict[str, Any]:
        """Convert classification into an execution gate decision."""
        blocked = risk_result.get("risk_level") in {"BLOCKED", "HIGH"}
        return {
            "blocked": blocked,
            "reason": "risk override" if blocked else "risk accepted",
            "risk_level": risk_result.get("risk_level", "UNKNOWN"),
        }
