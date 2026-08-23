"""Governance engine facade."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .canonical_resolver import CanonicalResolver


class GovernanceEngine:
    """Coordinate governance decisions without bypassing the risk gate."""

    def __init__(self, resolver: CanonicalResolver | None = None):
        self.resolver = resolver or CanonicalResolver()

    def select_canonical(
        self,
        artifact_type: str,
        artifacts: Iterable[Mapping[str, Any]],
        risk_result: Mapping[str, Any],
    ) -> dict[str, Any]:
        if risk_result.get("risk_level") == "BLOCKED":
            return {
                "artifact_id": None,
                "status": "BLOCKED",
                "reason": "risk engine blocked proposal",
            }
        return self.resolver.resolve(artifact_type, artifacts)
