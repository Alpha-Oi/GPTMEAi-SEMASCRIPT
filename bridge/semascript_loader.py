"""Load SEMASCRIPT action documents from JSON files."""

import json
from pathlib import Path


def load_json_file(path):
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"JSON file not found: {target}")
    if not target.is_file():
        raise ValueError(f"JSON path is not a file: {target}")

    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {target}: {exc}") from exc


def load_action_document(path):
    document = load_json_file(path)
    if not isinstance(document, dict):
        raise ValueError(f"Action document must be a JSON object: {path}")
    return document
