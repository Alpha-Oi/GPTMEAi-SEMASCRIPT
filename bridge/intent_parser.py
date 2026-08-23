"""Intent parser for SEMASCRIPT action documents."""

from __future__ import annotations

from typing import Any, Mapping


class IntentParser:
    """Normalize already-canonical SEMASCRIPT intent into system actions."""

    def parse(self, document: Mapping[str, Any]) -> dict[str, Any]:
        data = dict(document)
        intent = dict(data.get("intent", {}))
        actions = [dict(action) for action in data.get("actions", [])]
        return {
            "source": data.get("source", {}),
            "intent": intent,
            "actions": actions,
            "dry_run": True,
        }
