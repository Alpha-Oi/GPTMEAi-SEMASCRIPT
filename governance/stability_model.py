"""Stability model for evolution-aware governance."""

from __future__ import annotations

from typing import Any, Mapping


class StabilityModel:
    """Compute deterministic stability scores."""

    def score(self, artifact: Mapping[str, Any]) -> float:
        metrics = dict(artifact.get("evolution_metrics", {}))
        if "evolution_score" in metrics:
            return float(metrics["evolution_score"])
        volatility = float(metrics.get("volatility", 0.5))
        return max(0.0, min(100.0, 100.0 - (volatility * 100.0)))
