"""Deterministic evolution engine."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


class EvolutionEngine:
    """Build semantic diffs and changesets."""

    def diff(self, state_a: Mapping[str, Any], state_b: Mapping[str, Any]) -> dict[str, Any]:
        keys_a = set(state_a)
        keys_b = set(state_b)
        modified = sorted(key for key in keys_a & keys_b if state_a[key] != state_b[key])
        return {
            "added": sorted(keys_b - keys_a),
            "removed": sorted(keys_a - keys_b),
            "modified": modified,
            "semantic_changes": [{"field": key, "type": self._semantic_type(key)} for key in modified],
        }

    def create_changeset(
        self,
        from_state: Mapping[str, Any],
        to_state: Mapping[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        diff = self.diff(from_state, to_state)
        payload = {"diff": diff, "reason": reason}
        return {
            "changeset_id": f"changeset::{self._hash(payload)[-16:]}",
            "reason": reason,
            "diff": diff,
        }

    def emit_event(self, changeset: Mapping[str, Any]) -> dict[str, Any]:
        changeset_id = str(changeset["changeset_id"])
        return {
            "event_id": f"event::{changeset_id}::evolution",
            "event_type": "EVOLUTION_CHANGESET_CREATED",
            "artifact_id": changeset_id,
            "payload": dict(changeset),
        }

    def _semantic_type(self, key: str) -> str:
        if "trust" in key:
            return "trust change"
        if "canonical" in key:
            return "governance change"
        if "event" in key:
            return "event replay change"
        return "structural change"

    def _hash(self, value: Mapping[str, Any]) -> str:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
