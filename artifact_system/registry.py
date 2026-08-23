"""Artifact registry view over ARTIFACT_INDEX data."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


class ArtifactRegistry:
    """Read-only artifact lookup registry."""

    def __init__(self, artifacts: Iterable[Mapping[str, Any]]):
        self._artifacts = {str(item["id"]): dict(item) for item in artifacts}

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        artifact = self._artifacts.get(artifact_id)
        return dict(artifact) if artifact else None

    def by_type(self, artifact_type: str) -> list[dict[str, Any]]:
        return sorted(
            (dict(item) for item in self._artifacts.values() if item.get("type") == artifact_type),
            key=lambda item: str(item.get("id", "")),
        )
