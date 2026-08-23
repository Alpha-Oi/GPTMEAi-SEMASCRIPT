"""Check schema, compatibility matrix, and matrix documentation consistency."""

import json
from pathlib import Path
import sys


SCHEMA_SECTIONS = {
    "semascript_action_document": "semascript_action_document.schema.json",
    "planner_preview": "gptmeai_planner_preview.schema.json",
    "execution_approval": "execution_approval.schema.json",
    "adapter_error_model": "adapter_error_model.schema.json",
    "gptmeai_readonly_status_snapshot": "gptmeai_readonly_status_snapshot.schema.json",
}

REQUIRED_UNSUPPORTED_V0_1 = {
    "real execution",
    "memory mutation",
    "storage mutation",
    "ledger mutation",
    "runtime mutation",
    "dependency installation",
}


def project_root():
    return Path(__file__).resolve().parents[1]


def load_json(path):
    json_path = Path(path)
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON file not found: {json_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {json_path}: {exc}") from exc


def schema_required_fields(schema):
    required = schema.get("required", [])
    if not isinstance(required, list):
        return set()
    return {str(field) for field in required}


def _normalize_field_name(name):
    return str(name).strip().removesuffix("[]")


def _section_value(matrix, section):
    current = matrix
    for part in section.split("."):
        if not isinstance(current, dict) or part not in current:
            return {}
        current = current[part]
    return current if isinstance(current, dict) else {}


def matrix_field_names(matrix, section):
    fields = _section_value(matrix, section).get("fields", [])
    if not isinstance(fields, list):
        return set()
    return {
        _normalize_field_name(field.get("name", ""))
        for field in fields
        if isinstance(field, dict) and str(field.get("name", "")).strip()
    }


def unsupported_items(matrix):
    unsupported = matrix.get("unsupported_v0_1", [])
    if not isinstance(unsupported, list):
        return set()
    return {
        str(item.get("name", "")).strip()
        for item in unsupported
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }


def _unsupported_entries(matrix):
    entries = matrix.get("unsupported_v0_1", [])
    return entries if isinstance(entries, list) else []


def _supported_unsupported_entries(matrix):
    violations = []
    for item in _unsupported_entries(matrix):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        status = str(item.get("status", "")).strip().lower()
        if name in REQUIRED_UNSUPPORTED_V0_1 and status == "supported":
            violations.append(name)
    return violations


def _docs_text(project_root_path):
    docs_path = Path(project_root_path) / "docs" / "05_CONTRACT_COMPATIBILITY_MATRIX.md"
    try:
        return docs_path.read_text(encoding="utf-8").lower()
    except FileNotFoundError:
        return ""


def check_consistency(project_root_path):
    root = Path(project_root_path)
    contracts = root / "contracts"
    matrix = load_json(contracts / "compatibility_matrix.v0.1.json")
    errors = []
    warnings = []

    if matrix.get("scope") != "dry-run":
        errors.append("matrix scope must be dry-run")

    for section, filename in SCHEMA_SECTIONS.items():
        schema = load_json(contracts / filename)
        required = schema_required_fields(schema)
        fields = matrix_field_names(matrix, section)
        missing = sorted(required - fields)
        if missing:
            errors.append(f"{section} missing required fields: {', '.join(missing)}")

    unsupported = unsupported_items(matrix)
    missing_unsupported = sorted(REQUIRED_UNSUPPORTED_V0_1 - unsupported)
    if missing_unsupported:
        errors.append(
            "unsupported_v0_1 missing required boundaries: "
            + ", ".join(missing_unsupported)
        )

    supported_violations = _supported_unsupported_entries(matrix)
    if supported_violations:
        errors.append(
            "unsupported item is marked supported: "
            + ", ".join(sorted(supported_violations))
        )

    docs = _docs_text(root)
    if not docs:
        errors.append("docs/05_CONTRACT_COMPATIBILITY_MATRIX.md is missing")
    else:
        if "dry-run" not in docs:
            errors.append("compatibility matrix docs must mention dry-run")
        for item in sorted(REQUIRED_UNSUPPORTED_V0_1):
            if item not in docs:
                errors.append(f"compatibility matrix docs missing unsupported item: {item}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]) if args else project_root()
    try:
        result = check_consistency(root)
    except (FileNotFoundError, ValueError) as exc:
        print("SCHEMA_CONSISTENCY=FAIL")
        print(str(exc))
        return 1

    if result["ok"]:
        print("SCHEMA_CONSISTENCY=OK")
        print(f"ROOT={root}")
        return 0

    print("SCHEMA_CONSISTENCY=FAIL")
    print(f"ROOT={root}")
    for error in result["errors"]:
        print(f"- {error}")
    for warning in result["warnings"]:
        print(f"- warning: {warning}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
