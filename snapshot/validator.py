"""Snapshot consistency validator."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .generator import SnapshotGenerator


class SnapshotValidator:
    """Validate that a snapshot matches event replay output."""

    def __init__(self, generator: SnapshotGenerator | None = None):
        self.generator = generator or SnapshotGenerator()

    def validate(
        self,
        event_log: Iterable[Mapping[str, Any]],
        snapshot: Mapping[str, Any],
    ) -> dict[str, Any]:
        expected = self.generator.generate(event_log)
        return {
            "valid": dict(snapshot).get("state_hash") == expected["state_hash"],
            "expected_state_hash": expected["state_hash"],
            "actual_state_hash": dict(snapshot).get("state_hash"),
        }
