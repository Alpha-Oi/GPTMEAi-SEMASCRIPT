"""Local approval gate objects for dry-run previews."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4


def _expires_at(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")


def require_approval(preview):
    """Return whether a planner preview is blocked behind approval."""
    if not isinstance(preview, dict):
        return True
    return bool(preview.get("required_approvals")) or preview.get("dry_run") is True


def approve_preview(preview_id, approved_by, scope):
    """Create a local approval object without enabling execution."""
    if not preview_id:
        raise ValueError("preview_id is required")
    if not approved_by:
        raise ValueError("approved_by is required")

    approval_scope = dict(scope or {})
    approval_scope.setdefault("mode", "dry_run_only")

    return {
        "approval_id": f"approval-{uuid4()}",
        "preview_id": preview_id,
        "approved": True,
        "approved_by": approved_by,
        "scope": approval_scope,
        "expires_at": _expires_at(),
        "metadata": {
            "adapter": "GPTMEAi-SEMASCRIPT",
            "v0_1_execution_enabled": False,
        },
    }


def deny_preview(preview_id, reason):
    """Create a local denial object for audit-friendly preview handling."""
    if not preview_id:
        raise ValueError("preview_id is required")
    if not reason:
        raise ValueError("reason is required")

    return {
        "approval_id": f"approval-{uuid4()}",
        "preview_id": preview_id,
        "approved": False,
        "approved_by": "",
        "scope": {"mode": "denied"},
        "expires_at": _expires_at(),
        "metadata": {
            "adapter": "GPTMEAi-SEMASCRIPT",
            "reason": reason,
            "v0_1_execution_enabled": False,
        },
    }
