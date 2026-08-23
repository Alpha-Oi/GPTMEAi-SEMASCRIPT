"""Replay facade for state reconstruction."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .state_rebuilder import StateRebuilder


class ReplayEngine:
    """Replay event history into derived state."""

    def __init__(self, rebuilder: StateRebuilder | None = None):
        self.rebuilder = rebuilder or StateRebuilder()

    def replay(self, event_log: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        return self.rebuilder.rebuild(event_log)
