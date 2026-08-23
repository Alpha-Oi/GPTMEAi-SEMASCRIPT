"""Minimal SEMASCRIPT to proposal bridge."""

from __future__ import annotations

from typing import Any, Mapping


class SEMASCRIPTBridge:
    """Transform SEMASCRIPT-like documents into dry-run system proposals."""

    def to_proposal(self, document: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(document, Mapping):
            raise ValueError("document must be a mapping")
        actions = [dict(action) for action in document.get("actions", [])]
        return {
            "proposal_id": str(document.get("proposal_id", "proposal::from-semascript")),
            "artifact_type": str(document.get("artifact_type", "implementation_root_skeleton")),
            "actions": [
                {
                    "operation": str(action.get("operation", action.get("type", "document"))),
                    "target": str(action.get("target", "artifacts")),
                }
                for action in actions
            ],
            "dry_run": True,
        }
