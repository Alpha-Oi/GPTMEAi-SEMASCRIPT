"""Deterministic state reconstruction from event history."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


class StateRebuilder:
    """Rebuild artifact state from event_log only."""

    def rebuild(self, event_log: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        events = self._ordered_events(event_log)
        artifacts: dict[str, dict[str, Any]] = {}
        canonical: dict[str, str] = {}

        for event in events:
            artifact_id = str(event["artifact_id"])
            artifact = artifacts.setdefault(
                artifact_id,
                {
                    "artifact_id": artifact_id,
                    "state": "CREATED",
                    "trust": {"level": "unknown"},
                    "integrity": {"validated": False},
                    "events": [],
                },
            )
            artifact["events"].append(event["event_id"])
            artifact["last_event_id"] = event["event_id"]

            event_type = event.get("event_type")
            if event_type == "ARTIFACT_CREATED":
                artifact["state"] = event.get("new_state", "CREATED")
                payload = event.get("payload") or event.get("event_payload") or {}
                if isinstance(payload, Mapping):
                    artifact["type"] = payload.get("type", artifact.get("type"))
            elif event_type in {"STATE_CHANGED", "ARTIFACT_SUPERSEDED"}:
                artifact["state"] = event.get("new_state", artifact["state"])
            elif event_type == "TRUST_UPDATED":
                artifact["trust"] = deepcopy(event.get("trust", artifact["trust"]))
            elif event_type == "INTEGRITY_VALIDATED":
                artifact["integrity"] = {"validated": True}
            elif event_type == "INTEGRITY_FAILED":
                artifact["integrity"] = {"validated": False}
                artifact["state"] = event.get("new_state", "UNTRUSTED")
            elif event_type == "CANONICAL_SELECTED":
                artifact["canonical"] = True
                artifact_type = artifact.get("type") or event.get("artifact_type")
                if artifact_type:
                    canonical[str(artifact_type)] = artifact_id
            elif event_type == "APPROVED_ACTION_RECORDED":
                artifact["state"] = event.get("new_state", "APPROVED")

        return {
            "artifacts": dict(sorted(artifacts.items())),
            "canonical": dict(sorted(canonical.items())),
            "event_count": len(events),
        }

    def _ordered_events(self, event_log: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
        return tuple(
            sorted(
                (dict(event) for event in event_log),
                key=lambda item: (int(item.get("sequence", 0)), str(item.get("event_id", ""))),
            )
        )
