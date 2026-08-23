"""Append-only event store implementation."""

from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType
from typing import Any, Iterable, Mapping


class EventStore:
    """In-memory append-only event log.

    The store is intentionally abstract and dependency-free. It enforces event
    identity uniqueness and deterministic sequence ordering, but it does not
    persist to disk. A production implementation can replace this class behind
    the same interface.
    """

    def __init__(self, initial_events: Iterable[Mapping[str, Any]] | None = None):
        self._events: list[Mapping[str, Any]] = []
        self._event_ids: set[str] = set()
        for event in initial_events or ():
            self.append(event)

    def append(self, event: Mapping[str, Any]) -> Mapping[str, Any]:
        """Append one event. Duplicate event IDs are rejected."""
        event_id = str(event.get("event_id", "")).strip()
        if not event_id:
            raise ValueError("event.event_id is required")
        if event_id in self._event_ids:
            raise ValueError(f"event already exists: {event_id}")

        stored = deepcopy(dict(event))
        stored.setdefault("sequence", len(self._events) + 1)
        self._events.append(MappingProxyType(stored))
        self._event_ids.add(event_id)
        return deepcopy(stored)

    def read_all(self) -> tuple[dict[str, Any], ...]:
        """Read events in deterministic append order."""
        ordered = sorted(
            (dict(event) for event in self._events),
            key=lambda item: (int(item.get("sequence", 0)), str(item.get("event_id", ""))),
        )
        return tuple(deepcopy(event) for event in ordered)

    def __len__(self) -> int:
        return len(self._events)
