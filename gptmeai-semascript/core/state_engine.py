"""Replay-derived state engine."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


class StateEngine:
    """Rebuild state only from events."""

    def __init__(self):
        self._state: dict[str, Any] = self._empty_state()

    def rebuild(self, event_log: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        """Replay events deterministically and cache the derived state."""
        events = self._ordered(event_log)
        state = self._empty_state()
        for event in events:
            event_type = event["event_type"]
            artifact_id = event["artifact_id"]
            payload = deepcopy(dict(event.get("payload", {})))
            state["event_ids"].append(event["event_id"])

            if event_type == "ARTIFACT_REGISTERED":
                artifact = {
                    "artifact_id": artifact_id,
                    "type": payload.get("type", "unknown"),
                    "state": payload.get("state", "CREATED"),
                    "trust": payload.get("trust", "unknown"),
                    "source_event_id": event["event_id"],
                }
                state["artifacts"][artifact_id] = artifact
            elif event_type == "STATE_TRANSITION":
                artifact = state["artifacts"].setdefault(
                    artifact_id,
                    {"artifact_id": artifact_id, "type": "unknown", "trust": "unknown"},
                )
                artifact["state"] = payload.get("state", artifact.get("state", "CREATED"))
                artifact["source_event_id"] = event["event_id"]
            elif event_type == "GOVERNANCE_DECISION":
                state["governance_decisions"][event["event_id"]] = payload
                canonical = payload.get("canonical_artifact_id")
                if canonical:
                    state["canonical"][payload.get("artifact_type", "unknown")] = canonical
            elif event_type == "APPROVED_ACTION_RECORDED":
                proposal_id = payload.get("proposal_id", artifact_id)
                state["proposals"][proposal_id] = {
                    "proposal_id": proposal_id,
                    "state": "APPROVED",
                    "source_event_id": event["event_id"],
                }
            elif event_type == "EXECUTION_REJECTED":
                proposal_id = payload.get("proposal_id", artifact_id)
                state["proposals"][proposal_id] = {
                    "proposal_id": proposal_id,
                    "state": "REJECTED",
                    "source_event_id": event["event_id"],
                }

        state["events_applied"] = len(events)
        self._state = deepcopy(state)
        return deepcopy(state)

    def get_state(self) -> dict[str, Any]:
        """Return the last replay-derived state."""
        return deepcopy(self._state)

    def validate_replay_determinism(self, event_log: Iterable[Mapping[str, Any]]) -> bool:
        """Same event log must rebuild to the same state every time."""
        events = self._ordered(event_log)
        return self.rebuild(events) == self.rebuild(reversed(events))

    def _ordered(self, event_log: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            (deepcopy(dict(event)) for event in event_log),
            key=lambda item: (int(item.get("sequence", 0)), str(item.get("event_id", ""))),
        )

    def _empty_state(self) -> dict[str, Any]:
        return {
            "artifacts": {},
            "canonical": {},
            "proposals": {},
            "governance_decisions": {},
            "event_ids": [],
            "events_applied": 0,
        }
