"""Risk classifier facade."""

from __future__ import annotations

from typing import Any, Mapping

from .risk_scoring_model import RiskScoringModel


class RiskClassifier:
    """Classify proposals before approval or governance selection."""

    def __init__(self, scoring_model: RiskScoringModel | None = None):
        self.scoring_model = scoring_model or RiskScoringModel()

    def classify(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        scored = self.scoring_model.score(proposal)
        score = scored["score"]
        if scored["blockers"]:
            level = "BLOCKED"
        elif score >= 70:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
        return {
            "proposal_id": proposal.get("proposal_id", ""),
            "risk_level": level,
            "score": score,
            "blockers": scored["blockers"],
        }
