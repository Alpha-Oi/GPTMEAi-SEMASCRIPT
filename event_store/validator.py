"""Event validation for append-only logs."""

from __future__ import annotations

from typing import Any, Mapping


class EventValidator:
    """Validate the minimal event contract used by the skeleton."""

    REQUIRED_FIELDS = ("event_id", "event_type", "artifact_id")

    def validate(self, event: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(event, Mapping):
            raise ValueError("event must be a mapping")
        for field in self.REQUIRED_FIELDS:
            value = event.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"event.{field} must be a non-empty string")
        if "sequence" in event and not isinstance(event["sequence"], int):
            raise ValueError("event.sequence must be an integer when provided")
        return dict(event)
