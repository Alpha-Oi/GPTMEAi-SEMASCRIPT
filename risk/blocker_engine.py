"""Risk blocker enforcement."""

from __future__ import annotations

from typing import Any, Mapping


class BlockerEngine:
    """Enforce BLOCKED risk as an override for all flows."""

    def is_blocked(self, risk_result: Mapping[str, Any]) -> bool:
        return risk_result.get("risk_level") == "BLOCKED"
