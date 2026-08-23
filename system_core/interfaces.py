"""Service contracts for the modular GPTMEAi-SEMASCRIPT skeleton."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Protocol


class EventStoreProtocol(Protocol):
    """Append-only event store interface."""

    def append(self, event: Mapping[str, Any]) -> Mapping[str, Any]:
        """Append a validated event and return the stored immutable event."""

    def read_all(self) -> Iterable[Mapping[str, Any]]:
        """Read all events in deterministic order."""


class StateRebuilderProtocol(Protocol):
    """Replay-derived state builder interface."""

    def rebuild(self, event_log: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
        """Reconstruct state from event history only."""


class RiskClassifierProtocol(Protocol):
    """Risk gate interface."""

    def classify(self, proposal: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return deterministic proposal risk classification."""


class GovernanceResolverProtocol(Protocol):
    """Canonical artifact resolver interface."""

    def resolve(self, artifact_type: str, artifacts: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
        """Resolve one canonical artifact for a type."""
