"""Trust model for artifact governance."""

from __future__ import annotations

from typing import Any, Mapping


TRUST_SCORE = {"high": 3, "medium": 2, "low": 1, "unknown": 0}


class TrustModel:
    """Evaluate trust level and canonical eligibility."""

    def level(self, artifact: Mapping[str, Any]) -> str:
        return str(dict(artifact.get("trust", {})).get("level", "unknown"))

    def score(self, artifact: Mapping[str, Any]) -> int:
        return TRUST_SCORE.get(self.level(artifact), 0)

    def is_eligible(self, artifact: Mapping[str, Any]) -> bool:
        integrity = dict(artifact.get("integrity", {})).get("validated") is True
        return integrity and self.level(artifact) in {"high", "medium"}
