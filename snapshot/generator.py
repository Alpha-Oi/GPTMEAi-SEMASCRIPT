"""Deterministic snapshot projection generator."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from state_engine import StateRebuilder
from system_core import canonical_hash


class SnapshotGenerator:
    """Generate read-only projection snapshots from replay-derived state."""

    def __init__(self, rebuilder: StateRebuilder | None = None):
        self.rebuilder = rebuilder or StateRebuilder()

    def generate(self, event_log: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        ordered_events = tuple(event_log)
        state = self.rebuilder.rebuild(ordered_events)
        state_hash = canonical_hash(state)
        cursor = ordered_events[-1]["event_id"] if ordered_events else "event::none"
        return {
            "snapshot_id": f"snapshot::{cursor}::{state_hash[-12:]}",
            "event_cursor": cursor,
            "state_hash": state_hash,
            "system_state": state,
            "projection_only": True,
        }
