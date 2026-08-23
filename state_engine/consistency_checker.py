"""Consistency checks for reconstructed state."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .state_rebuilder import StateRebuilder


class ConsistencyChecker:
    """Compare current state caches with replay-derived state."""

    def __init__(self, rebuilder: StateRebuilder | None = None):
        self.rebuilder = rebuilder or StateRebuilder()

    def check(
        self,
        event_log: Iterable[Mapping[str, Any]],
        current_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        rebuilt = self.rebuilder.rebuild(event_log)
        return {
            "consistent": rebuilt == dict(current_state),
            "rebuilt_state": rebuilt,
            "current_state": dict(current_state),
        }
