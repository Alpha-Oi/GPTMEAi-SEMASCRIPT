"""Closed evolution loop validator."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from cognition import CognitiveInterpreter
from snapshot import SnapshotGenerator, SnapshotValidator


class LoopValidator:
    """Validate replay, snapshot, and mental model determinism."""

    def __init__(
        self,
        snapshot_generator: SnapshotGenerator | None = None,
        snapshot_validator: SnapshotValidator | None = None,
        interpreter: CognitiveInterpreter | None = None,
    ):
        self.snapshot_generator = snapshot_generator or SnapshotGenerator()
        self.snapshot_validator = snapshot_validator or SnapshotValidator(self.snapshot_generator)
        self.interpreter = interpreter or CognitiveInterpreter()

    def validate(
        self,
        event_log: Iterable[Mapping[str, Any]],
        snapshot: Mapping[str, Any],
    ) -> dict[str, Any]:
        events = tuple(event_log)
        snapshot_result = self.snapshot_validator.validate(events, snapshot)
        mental_a = self.interpreter.interpret(snapshot)
        mental_b = self.interpreter.interpret(snapshot)
        return {
            "valid": snapshot_result["valid"] and mental_a == mental_b,
            "snapshot": snapshot_result,
            "mental_model_deterministic": mental_a == mental_b,
        }
