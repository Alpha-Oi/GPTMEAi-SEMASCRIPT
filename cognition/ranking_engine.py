"""Deterministic candidate ranking."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


TRUST_RANK = {"high": 3, "medium": 2, "low": 1, "unknown": 0}


class RankingEngine:
    """Rank candidates without randomness or external inputs."""

    def rank(self, candidates: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            (dict(candidate) for candidate in candidates),
            key=lambda item: (
                item.get("eligible") is True,
                TRUST_RANK.get(str(item.get("trust", "unknown")), 0),
                str(item.get("state", "")) == "ACTIVE",
                str(item.get("artifact_id", "")),
            ),
            reverse=True,
        )
