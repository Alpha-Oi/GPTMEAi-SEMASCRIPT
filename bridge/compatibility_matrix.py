"""Load and query the v0.1 contract compatibility matrix."""

import json
from pathlib import Path


DEFAULT_MATRIX_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "compatibility_matrix.v0.1.json"
)


def load_compatibility_matrix(path=None) -> dict:
    """Load the machine-readable compatibility matrix."""
    matrix_path = DEFAULT_MATRIX_PATH if path is None else Path(path)
    if not matrix_path.is_file():
        raise FileNotFoundError(f"Compatibility matrix not found: {matrix_path}")

    try:
        return json.loads(matrix_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid compatibility matrix JSON: {matrix_path}: {exc}") from exc


def _section_fields(matrix, section):
    parts = section.split(".")
    current = matrix
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return []
        current = current[part]
    if isinstance(current, dict):
        fields = current.get("fields", [])
        return fields if isinstance(fields, list) else []
    return []


def get_field_status(matrix: dict, section: str, field_name: str) -> dict | None:
    """Return the field entry for a section, or None when absent."""
    for field in _section_fields(matrix, section):
        if isinstance(field, dict) and field.get("name") == field_name:
            return field
    return None


def list_unsupported_v0_1(matrix: dict) -> list:
    """Return the explicit v0.1 non-support list."""
    unsupported = matrix.get("unsupported_v0_1", [])
    return unsupported if isinstance(unsupported, list) else []
