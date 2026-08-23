"""ARTIFACT_INDEX loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ArtifactIndexLoader:
    """Load ARTIFACT_INDEX JSON without mutating it."""

    def load(self, path: str | Path) -> dict[str, Any]:
        index_path = Path(path)
        data = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("ARTIFACT_INDEX must be a JSON object")
        return data
