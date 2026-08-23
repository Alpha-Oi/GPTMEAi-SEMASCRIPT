"""Read-only hooks into evolution graph metadata."""

from __future__ import annotations

from typing import Any, Mapping


class EvolutionGraphReferenceHooks:
    """Expose evolution graph references without modifying them."""

    def outgoing(self, index: Mapping[str, Any], artifact_id: str) -> list[dict[str, Any]]:
        graph = dict(dict(index.get("diff_engine", {})).get("evolution_graph", {}))
        edges = graph.get("edges", [])
        return sorted(
            (dict(edge) for edge in edges if edge.get("from") == artifact_id),
            key=lambda edge: (str(edge.get("to", "")), str(edge.get("changeset_id", ""))),
        )

    def incoming(self, index: Mapping[str, Any], artifact_id: str) -> list[dict[str, Any]]:
        graph = dict(dict(index.get("diff_engine", {})).get("evolution_graph", {}))
        edges = graph.get("edges", [])
        return sorted(
            (dict(edge) for edge in edges if edge.get("to") == artifact_id),
            key=lambda edge: (str(edge.get("from", "")), str(edge.get("changeset_id", ""))),
        )
