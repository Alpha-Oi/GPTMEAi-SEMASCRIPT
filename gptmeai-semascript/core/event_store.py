"""Append-only deterministic event store."""

from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType
from typing import Any, Mapping


class EventStore:
    """In-memory append-only event log.

    This store is the only source of truth for the bootstrap implementation.
    It has no delete, update, or overwrite operation.
    """

    REQUIRED_FIELDS = ("event_id", "event_type", "artifact_id")

    def __init__(self, initial_events: list[Mapping[str, Any]] | None = None):
        self._events: list[Mapping[str, Any]] = []
        self._event_ids: set[str] = set()
        for event in initial_events or []:
            self.append(event)

    def append(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Append one immutable event and return a defensive copy."""
        validated = self.validate_event(event)
        event_id = validated["event_id"]
        if event_id in self._event_ids:
            raise ValueError(f"event already exists: {event_id}")

        stored = deepcopy(validated)
        stored["sequence"] = len(self._events) + 1
        self._events.append(MappingProxyType(stored))
        self._event_ids.add(event_id)
        return deepcopy(stored)

    def get_all(self) -> list[dict[str, Any]]:
        """Return events in deterministic append order as defensive copies."""
        return [
            deepcopy(dict(event))
            for event in sorted(
                self._events,
                key=lambda item: (int(item.get("sequence", 0)), str(item.get("event_id", ""))),
            )
        ]

    def validate_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Validate minimal event shape."""
        if not isinstance(event, Mapping):
            raise ValueError("event must be a mapping")
        for field in self.REQUIRED_FIELDS:
            value = event.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if "sequence" in event:
            raise ValueError("sequence is assigned by EventStore and cannot be supplied")
        return deepcopy(dict(event))

    def enforce_immutability(self) -> bool:
        """Return true when internal event identities are unique and ordered."""
        event_ids = [event["event_id"] for event in self._events]
        sequences = [event["sequence"] for event in self._events]
        return len(event_ids) == len(set(event_ids)) and sequences == list(range(1, len(sequences) + 1))

    def __len__(self) -> int:
        return len(self._events)
