"""Semantic diff engine."""

from __future__ import annotations

from typing import Any, Mapping


class DiffEngine:
    """Compute deterministic semantic diffs between reconstructed states."""

    def compute_diff(self, state_a: Mapping[str, Any], state_b: Mapping[str, Any]) -> dict[str, Any]:
        keys_a = set(state_a)
        keys_b = set(state_b)
        added = sorted(keys_b - keys_a)
        removed = sorted(keys_a - keys_b)
        modified = sorted(key for key in keys_a & keys_b if state_a[key] != state_b[key])
        unchanged = sorted(key for key in keys_a & keys_b if state_a[key] == state_b[key])
        semantic_changes = [
            {"field": key, "classification": self._classify_change(key)}
            for key in modified
        ]
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged,
            "semantic_changes": semantic_changes,
        }

    def _classify_change(self, key: str) -> str:
        if "trust" in key:
            return "trust change"
        if "integrity" in key:
            return "integrity change"
        if "state" in key:
            return "lifecycle change"
        if "lineage" in key:
            return "lineage change"
        return "structural change"
