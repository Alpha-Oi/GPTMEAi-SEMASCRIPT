"""Dry-run preview generator facade."""

from __future__ import annotations

from typing import Any, Mapping

from .planner_preview_adapter import map_semascript_to_planner_preview


class PreviewGenerator:
    """Generate GPTMEAi planner previews without execution."""

    def generate(self, document: Mapping[str, Any]) -> dict[str, Any]:
        preview = map_semascript_to_planner_preview(dict(document))
        preview["dry_run"] = True
        return preview
