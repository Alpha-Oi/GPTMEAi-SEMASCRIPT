"""Evolution graph reference manager."""

from __future__ import annotations

from typing import Any, Mapping


class EvolutionGraphManager:
    """Maintain deterministic graph nodes and edges for artifact evolution."""

    def __init__(self):
        self.nodes: set[str] = set()
        self.edges: list[dict[str, Any]] = []

    def add_transition(
        self,
        from_artifact: str,
        to_artifact: str,
        changeset_id: str,
        diff_type: str = "minor",
    ) -> dict[str, Any]:
        self.nodes.update({from_artifact, to_artifact})
        edge = {
            "from": from_artifact,
            "to": to_artifact,
            "changeset_id": changeset_id,
            "diff_type": diff_type,
        }
        self.edges.append(edge)
        self.edges = sorted(self.edges, key=lambda item: (item["from"], item["to"], item["changeset_id"]))
        return dict(edge)

    def export(self) -> dict[str, Any]:
        return {"nodes": sorted(self.nodes), "edges": [dict(edge) for edge in self.edges]}
