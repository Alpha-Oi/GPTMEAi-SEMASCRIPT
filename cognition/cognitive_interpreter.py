"""Deterministic executable mental model interpreter."""

from __future__ import annotations

from typing import Any, Mapping

from system_core import canonical_hash


class CognitiveInterpreter:
    """Interpret a system snapshot into cognitive decision semantics."""

    def interpret(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        state = dict(snapshot.get("system_state", {}))
        artifacts = state.get("artifacts", {})
        interpretations = {}
        for artifact_id, artifact in sorted(dict(artifacts).items()):
            trust = dict(artifact.get("trust", {})).get("level", "unknown")
            integrity = dict(artifact.get("integrity", {})).get("validated") is True
            interpretations[artifact_id] = {
                "trust_semantics": trust,
                "integrity_semantics": "validated" if integrity else "unvalidated",
                "state_semantics": artifact.get("state", "unknown"),
            }

        model = {
            "model_type": "EXECUTABLE_MENTAL_MODEL",
            "derived_from_snapshot_id": snapshot.get("snapshot_id"),
            "artifact_interpretations": interpretations,
            "deterministic": True,
        }
        model["model_id"] = f"mental-model::{canonical_hash(model)[-12:]}"
        return model
