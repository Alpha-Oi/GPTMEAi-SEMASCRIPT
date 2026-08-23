"""Validated event writer facade."""

from __future__ import annotations

from typing import Any, Mapping

from .store import EventStore
from .validator import EventValidator


class EventWriter:
    """Write validated events to an append-only store."""

    def __init__(self, event_store: EventStore, validator: EventValidator | None = None):
        self.event_store = event_store
        self.validator = validator or EventValidator()

    def append(self, event: Mapping[str, Any]) -> Mapping[str, Any]:
        validated = self.validator.validate(event)
        return self.event_store.append(validated)
