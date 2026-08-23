"""Drift detection for snapshot projections."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from snapshot import SnapshotValidator


class DriftDetector:
    """Detect snapshot drift against replay-derived state."""

    def __init__(self, snapshot_validator: SnapshotValidator | None = None):
        self.snapshot_validator = snapshot_validator or SnapshotValidator()

    def detect(
        self,
        event_log: Iterable[Mapping[str, Any]],
        snapshot: Mapping[str, Any],
    ) -> dict[str, Any]:
        result = self.snapshot_validator.validate(event_log, snapshot)
        return {
            "drift_detected": not result["valid"],
            "reason": "SNAPSHOT_MISMATCH" if not result["valid"] else "NONE",
            "details": result,
        }
