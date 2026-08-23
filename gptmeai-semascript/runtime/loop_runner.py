"""Deterministic loop runner."""

from __future__ import annotations

from core.event_store import EventStore

from .orchestrator import Orchestrator


class LoopRunner:
    """Run deterministic closed-loop cycles."""

    def __init__(self, event_store: EventStore | None = None):
        self.event_store = event_store or EventStore()
        self.orchestrator = Orchestrator(self.event_store)

    def run_cycles(self, cycles: int = 3) -> dict[str, object]:
        results = []
        for cycle in range(1, cycles + 1):
            results.append(self.orchestrator.run_cycle(cycle))
        return {
            "cycles": cycles,
            "loop_status": "STABLE",
            "results": results,
            "events": self.event_store.get_all(),
        }
