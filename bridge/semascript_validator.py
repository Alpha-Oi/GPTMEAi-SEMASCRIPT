"""Manual SEMASCRIPT action document validator."""

REQUIRED_TOP_LEVEL_FIELDS = (
    "version",
    "source",
    "intent",
    "actions",
    "constraints",
    "safety",
    "metadata",
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _add_type_error(errors, field, expected):
    errors.append({"field": field, "message": f"Expected {expected}."})


def validate_action_document(document):
    """Validate the v0.1 canonical SEMASCRIPT action document shape.

    This deliberately avoids external JSON Schema packages. Contracts remain
    the source of truth; this function enforces the safety-critical subset.
    """
    errors = []
    warnings = []

    if not isinstance(document, dict):
        return {
            "valid": False,
            "errors": [{"field": "$", "message": "Document must be an object."}],
            "warnings": [],
        }

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in document:
            errors.append({"field": field, "message": "Missing required field."})

    if not _is_non_empty_string(document.get("version")):
        _add_type_error(errors, "version", "non-empty string")

    source = document.get("source")
    if not isinstance(source, dict):
        _add_type_error(errors, "source", "object")
    elif source.get("system") != "SEMASCRIPT":
        errors.append({"field": "source.system", "message": "Expected 'SEMASCRIPT'."})

    intent = document.get("intent")
    if not isinstance(intent, dict):
        _add_type_error(errors, "intent", "object")
    elif not _is_non_empty_string(intent.get("summary")):
        _add_type_error(errors, "intent.summary", "non-empty string")

    actions = document.get("actions")
    if not isinstance(actions, list):
        _add_type_error(errors, "actions", "array")
    elif not actions:
        errors.append({"field": "actions", "message": "At least one action is required."})
    else:
        for index, action in enumerate(actions):
            prefix = f"actions[{index}]"
            if not isinstance(action, dict):
                _add_type_error(errors, prefix, "object")
                continue
            for field in ("id", "type", "description"):
                if not _is_non_empty_string(action.get(field)):
                    _add_type_error(errors, f"{prefix}.{field}", "non-empty string")

    if not isinstance(document.get("constraints"), dict):
        _add_type_error(errors, "constraints", "object")

    safety = document.get("safety")
    if not isinstance(safety, dict):
        _add_type_error(errors, "safety", "object")
    else:
        if safety.get("dry_run_only") is not True:
            errors.append({"field": "safety.dry_run_only", "message": "v0.1 requires true."})
        if safety.get("requires_approval") is not True:
            errors.append({"field": "safety.requires_approval", "message": "v0.1 requires true."})
        forbidden = safety.get("forbidden_operations")
        if forbidden is None:
            warnings.append(
                {
                    "field": "safety.forbidden_operations",
                    "message": "Recommended for explicit mutation boundaries.",
                }
            )
        elif not isinstance(forbidden, list) or not all(isinstance(item, str) for item in forbidden):
            _add_type_error(errors, "safety.forbidden_operations", "array of strings")

    if not isinstance(document.get("metadata"), dict):
        _add_type_error(errors, "metadata", "object")

    return {"valid": not errors, "errors": errors, "warnings": warnings}
