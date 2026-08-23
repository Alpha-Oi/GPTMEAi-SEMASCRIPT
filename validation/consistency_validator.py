"""System consistency validator."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from state_engine import ConsistencyChecker


class ConsistencyValidator:
    """Validate replay consistency and derived caches."""

    def __init__(self, checker: ConsistencyChecker | None = None):
        self.checker = checker or ConsistencyChecker()

    def validate_state(
        self,
        event_log: Iterable[Mapping[str, Any]],
        current_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        return self.checker.check(event_log, current_state)
