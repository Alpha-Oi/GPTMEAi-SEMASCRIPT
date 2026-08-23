"""Deterministic decision flow for cognitive model outputs."""

from __future__ import annotations

from typing import Any, Mapping


class DecisionFlowEngine:
    """Build ordered decision candidates from an executable mental model."""

    def evaluate(self, mental_model: Mapping[str, Any]) -> dict[str, Any]:
        interpretations = dict(mental_model.get("artifact_interpretations", {}))
        candidates = []
        for artifact_id, semantics in sorted(interpretations.items()):
            candidates.append(
                {
                    "artifact_id": artifact_id,
                    "eligible": semantics.get("integrity_semantics") == "validated",
                    "trust": semantics.get("trust_semantics", "unknown"),
                    "state": semantics.get("state_semantics", "unknown"),
                }
            )
        return {
            "model_id": mental_model.get("model_id"),
            "candidates": candidates,
            "ordering": "artifact_id ascending",
        }
