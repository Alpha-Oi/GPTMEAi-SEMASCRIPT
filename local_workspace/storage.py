"""UTF-8 loading and same-filesystem atomic storage for Local Workspace v1."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .model import LocalWorkspaceError, canonical_json, empty_document, validate_document


def workspace_path(value: str | os.PathLike[str]) -> Path:
    """Convert a local filesystem value into a path and reject URLs/UNC paths."""
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw:
        raise LocalWorkspaceError("INVALID_ARGUMENT", "workspace path is required")
    if "://" in raw or raw.startswith(("\\\\", "//")):
        raise LocalWorkspaceError(
            "INVALID_ARGUMENT",
            "workspace path must be a local filesystem path, not a URL or network path",
        )
    return Path(raw)


def load_workspace(value: str | os.PathLike[str]) -> dict[str, Any]:
    """Load and validate one Local Workspace v1 JSON file."""
    path = workspace_path(value)
    if not path.exists():
        raise LocalWorkspaceError(
            "WORKSPACE_NOT_FOUND",
            f"workspace not found: {path}",
        )
    if not path.is_file():
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"workspace path is not a file: {path}",
        )

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise LocalWorkspaceError(
            "INVALID_JSON",
            f"workspace is not valid UTF-8 JSON: {path}",
        ) from exc
    except OSError as exc:
        raise LocalWorkspaceError(
            "INVALID_WORKSPACE",
            f"workspace could not be read: {path}",
        ) from exc

    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LocalWorkspaceError(
            "INVALID_JSON",
            f"workspace contains invalid JSON at line {exc.lineno}, column {exc.colno}",
        ) from exc
    return validate_document(document)


def atomic_save(
    document: Any,
    value: str | os.PathLike[str],
    *,
    require_absent: bool = False,
) -> dict[str, Any]:
    """Validate and atomically replace a workspace through a sibling temp file."""
    path = workspace_path(value)
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        raise LocalWorkspaceError(
            "INVALID_ARGUMENT",
            f"workspace parent directory must already exist: {parent}",
        )
    if require_absent and os.path.lexists(path):
        raise LocalWorkspaceError(
            "WORKSPACE_ALREADY_EXISTS",
            f"workspace already exists: {path}",
        )

    canonical = validate_document(document)
    serialized = canonical_json(canonical)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())

        if require_absent and os.path.lexists(path):
            raise LocalWorkspaceError(
                "WORKSPACE_ALREADY_EXISTS",
                f"workspace already exists: {path}",
            )
        os.replace(temporary_path, path)
        temporary_path = None
    except LocalWorkspaceError:
        raise
    except OSError as exc:
        raise LocalWorkspaceError(
            "WRITE_FAILED",
            f"workspace write failed: {path}",
        ) from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

    return canonical


def init_workspace(value: str | os.PathLike[str]) -> dict[str, Any]:
    """Create a new empty workspace and never overwrite an existing path."""
    return atomic_save(empty_document(), value, require_absent=True)
