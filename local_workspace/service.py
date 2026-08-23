"""Use cases for persistent Local Workspace v1 files."""

from __future__ import annotations

from copy import deepcopy
import os
from typing import Any

from .model import LocalWorkspaceError, validate_document
from .storage import atomic_save, init_workspace, load_workspace


class LocalWorkspaceService:
    """Deterministic init/add/list/search/validate operations."""

    def init(self, path: str | os.PathLike[str]) -> dict[str, Any]:
        return init_workspace(path)

    def add(
        self,
        path: str | os.PathLike[str],
        artifact_id: str,
        title: str,
        content: str,
    ) -> dict[str, Any]:
        document = load_workspace(path)
        artifact = self._argument_artifact(artifact_id, title, content)

        if any(
            existing["artifact_id"] == artifact["artifact_id"]
            for existing in document["artifacts"]
        ):
            raise LocalWorkspaceError(
                "DUPLICATE_ARTIFACT_ID",
                f"duplicate artifact_id: {artifact['artifact_id']}",
            )

        updated = {
            "format": document["format"],
            "version": document["version"],
            "artifacts": [*document["artifacts"], artifact],
        }
        validated = validate_document(updated)
        return atomic_save(validated, path)

    def list_artifacts(self, path: str | os.PathLike[str]) -> list[dict[str, str]]:
        document = load_workspace(path)
        return deepcopy(document["artifacts"])

    def search(
        self,
        path: str | os.PathLike[str],
        query: str,
    ) -> list[dict[str, str]]:
        if not isinstance(query, str) or not query.strip():
            raise LocalWorkspaceError(
                "INVALID_ARGUMENT",
                "search query must be non-empty after trimming",
            )
        folded_query = query.casefold()
        artifacts = self.list_artifacts(path)
        return [
            artifact
            for artifact in artifacts
            if any(
                folded_query in artifact[field].casefold()
                for field in ("artifact_id", "title", "content")
            )
        ]

    def validate(self, path: str | os.PathLike[str]) -> dict[str, Any]:
        return load_workspace(path)

    @staticmethod
    def _argument_artifact(
        artifact_id: str,
        title: str,
        content: str,
    ) -> dict[str, str]:
        for name, value in (
            ("artifact_id", artifact_id),
            ("title", title),
            ("content", content),
        ):
            if not isinstance(value, str):
                raise LocalWorkspaceError(
                    "INVALID_ARGUMENT",
                    f"{name} must be a string",
                )
        if not artifact_id.strip():
            raise LocalWorkspaceError(
                "INVALID_ARGUMENT",
                "artifact_id must be non-empty after trimming",
            )
        if not title.strip():
            raise LocalWorkspaceError(
                "INVALID_ARGUMENT",
                "title must be non-empty after trimming",
            )
        if content == "":
            raise LocalWorkspaceError(
                "INVALID_ARGUMENT",
                "content must be non-empty",
            )
        return {
            "artifact_id": artifact_id.strip(),
            "title": title.strip(),
            "content": content,
        }
