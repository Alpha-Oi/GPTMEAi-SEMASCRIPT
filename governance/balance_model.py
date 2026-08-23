"""Dual-objective balance model."""

from __future__ import annotations

from typing import Any, Mapping


class BalanceModel:
    """Score stability and innovation as one deterministic value."""

    def final_score(self, artifact: Mapping[str, Any]) -> float:
        metrics = dict(artifact.get("balance_metrics", {}))
        if "final_score" in metrics:
            return float(metrics["final_score"])
        stability = float(metrics.get("stability_score", 0))
        innovation = float(metrics.get("innovation_score", 0))
        return (0.6 * stability) + (0.4 * innovation)
