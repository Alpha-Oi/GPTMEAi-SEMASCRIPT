"""Local Workspace v1 format validation and canonical serialization."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Mapping


FORMAT_NAME = "semantic-ai-os.local-workspace"
FORMAT_VERSION = 1
TOP_LEVEL_KEYS = frozenset({"format", "version", "artifacts"})
ARTIFACT_KEYS = frozenset({"artifact_id", "title", "content"})


class LocalWorkspaceError(Exception):
    """Expected workspace, argument, or storage error with a stable code."""

    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


def empty_document() -> dict[str, Any]:
    """Return a new empty Local Workspace v1 document."""
    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "artifacts": [],
    }


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: frozenset[str],
    location: str,
) -> None:
    actual = set(value)
    if actual == expected:
        return

    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    details = []
    if missing:
        details.append("missing keys: " + ", ".join(missing))
    if unknown:
        details.append("unknown keys: " + ", ".join(unknown))
    raise LocalWorkspaceError(
        "INVALID_WORKSPACE",
        f"{location} has invalid structure ({'; '.join(details)})",
    )


def _canonical_artifact(value: Any, index: int) -> dict[str, str]:
    location = f"artifacts[{index}]"
    if not isinstance(value, dict):
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"{location} must be an object",
        )
    _require_exact_keys(value, ARTIFACT_KEYS, location)

    artifact_id = value["artifact_id"]
    title = value["title"]
    content = value["content"]
    for field_name, field_value in (
        ("artifact_id", artifact_id),
        ("title", title),
        ("content", content),
    ):
        if not isinstance(field_value, str):
            raise LocalWorkspaceError(
                "INVALID_WORKSPACE",
                f"{location}.{field_name} must be a string",
            )

    normalized_id = artifact_id.strip()
    normalized_title = title.strip()
    if not normalized_id:
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"{location}.artifact_id must be non-empty after trimming",
        )
    if not normalized_title:
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"{location}.title must be non-empty after trimming",
        )
    if content == "":
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"{location}.content must be non-empty",
        )

    return {
        "artifact_id": normalized_id,
        "title": normalized_title,
        "content": content,
    }


def validate_document(document: Any) -> dict[str, Any]:
    """Validate and return a canonical independent document copy."""
    if not isinstance(document, dict):
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            "workspace must be exactly one JSON object",
        )
    _require_exact_keys(document, TOP_LEVEL_KEYS, "workspace")

    if document["format"] != FORMAT_NAME:
        raise LocalWorkspaceError(
            "UNSUPPORTED_WORKSPACE_FORMAT",
            f"unsupported workspace format: {document['format']!r}",
        )

    version = document["version"]
    if type(version) is not int:
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            "workspace.version must be integer 1",
        )
    if version != FORMAT_VERSION:
        raise LocalWorkspaceError(
            "UNSUPPORTED_WORKSPACE_VERSION",
            f"unsupported workspace version: {version}",
        )

    artifacts = document["artifacts"]
    if not isinstance(artifacts, list):
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            "workspace.artifacts must be a list",
        )

    canonical_artifacts = [
        _canonical_artifact(artifact, index)
        for index, artifact in enumerate(artifacts)
    ]
    canonical_artifacts.sort(key=lambda artifact: artifact["artifact_id"])

    seen_ids: set[str] = set()
    for artifact in canonical_artifacts:
        artifact_id = artifact["artifact_id"]
        if artifact_id in seen_ids:
            raise LocalWorkspaceError(
                "DUPLICATE_ARTIFACT_ID",
                f"duplicate artifact_id: {artifact_id}",
            )
        seen_ids.add(artifact_id)

    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "artifacts": deepcopy(canonical_artifacts),
    }


def canonical_json(document: Any) -> str:
    """Serialize a validated document deterministically as UTF-8 JSON text."""
    canonical = validate_document(document)
    return json.dumps(canonical, ensure_ascii=False, indent=2) + "\n"
