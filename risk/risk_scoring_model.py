"""Deterministic risk scoring model."""

from __future__ import annotations

from typing import Any, Mapping


BLOCKED_OPERATIONS = {
    "bypass_governance",
    "bypass_risk",
    "direct_runtime_mutation",
    "mutate_memory",
    "mutate_runtime",
    "mutate_storage",
}
MEDIUM_OPERATIONS = {"delete", "network", "shell", "write"}


class RiskScoringModel:
    """Score proposals with fixed rules."""

    def score(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        actions = proposal.get("actions", [])
        blockers = []
        score = 10
        for action in actions if isinstance(actions, list) else []:
            operation = str(dict(action).get("operation", "")).strip().lower()
            if operation in BLOCKED_OPERATIONS:
                blockers.append({"operation": operation, "reason": "forbidden operation"})
                score = max(score, 100)
            elif operation in MEDIUM_OPERATIONS:
                score = max(score, 60)
        return {"score": score, "blockers": blockers}
