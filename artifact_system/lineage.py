"""Lineage tracking helpers."""

from __future__ import annotations

from typing import Any, Mapping


class LineageTracker:
    """Read lineage fields from artifact entries."""

    def chain_for(self, artifact: Mapping[str, Any]) -> list[str]:
        lineage = artifact.get("lineage", {})
        if not isinstance(lineage, Mapping):
            return []
        return list(lineage.get("chain", []))

    def depth_for(self, artifact: Mapping[str, Any]) -> int:
        lineage = artifact.get("lineage", {})
        if not isinstance(lineage, Mapping):
            return 0
        return int(lineage.get("depth", 0))
