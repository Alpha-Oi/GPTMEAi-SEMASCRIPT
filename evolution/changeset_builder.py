"""Deterministic changeset builder."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from system_core import canonical_hash

from .diff_engine import DiffEngine


class ChangesetBuilder:
    """Build semantic changesets between artifact states."""

    def __init__(self, diff_engine: DiffEngine | None = None):
        self.diff_engine = diff_engine or DiffEngine()

    def build(
        self,
        from_artifact: str,
        to_artifact: str,
        state_a: Mapping[str, Any],
        state_b: Mapping[str, Any],
        trigger_event_ids: Iterable[str],
    ) -> dict[str, Any]:
        diff = self.diff_engine.compute_diff(state_a, state_b)
        payload = {
            "from": from_artifact,
            "to": to_artifact,
            "diff": diff,
            "trigger_event_ids": sorted(trigger_event_ids),
        }
        return {
            "changeset_id": f"changeset::{canonical_hash(payload)[-12:]}",
            "from_artifact": from_artifact,
            "to_artifact": to_artifact,
            "diff": diff,
            "semantic_summary": "deterministic semantic changeset",
            "trigger_event_ids": sorted(trigger_event_ids),
        }
