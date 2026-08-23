"""Normalize SEMASCRIPT AST-like objects into action documents."""

REQUIRED_FIELDS = {"version", "source", "intent", "actions", "constraints", "safety", "metadata"}
SAFE_EXEC_ROOT_ACTION_TYPES = {
    "ASSERT_STATE": "assert_state",
    "CHANGE": "change",
    "DEPENDENCY": "dependency",
    "EXPAND": "expand",
    "OBSERVE": "observe",
}


def _normalize_source(source):
    if isinstance(source, dict):
        normalized = dict(source)
    elif source:
        normalized = {"system": str(source)}
    else:
        normalized = {}
    normalized.setdefault("system", "SEMASCRIPT")
    return normalized


def _normalize_intent(intent, ast_document):
    if isinstance(intent, dict):
        normalized = dict(intent)
    elif intent:
        normalized = {"summary": str(intent)}
    else:
        normalized = {"summary": str(ast_document.get("summary") or ast_document.get("goal") or "")}
    if not str(normalized.get("summary", "")).strip():
        normalized["summary"] = "Normalized SEMASCRIPT AST document"
    return normalized


def _normalize_actions(actions):
    if actions is None:
        actions = []
    if isinstance(actions, dict):
        actions = [actions]
    if not isinstance(actions, list):
        actions = [{"description": str(actions)}]

    normalized = []
    for index, action in enumerate(actions, start=1):
        if isinstance(action, str):
            item = {"description": action}
        elif isinstance(action, dict):
            item = dict(action)
        else:
            item = {"description": str(action)}
        item.setdefault("id", f"action-{index}")
        item.setdefault("type", item.get("operation", "inspect"))
        item.setdefault("description", item.get("summary", f"Normalized action {index}"))
        normalized.append(item)
    return normalized


def _ast_value_label(value):
    if not isinstance(value, dict):
        return str(value)

    kind = value.get("kind")
    if kind == "node":
        class_name = str(value.get("class_name", "")).strip()
        root = str(value.get("root", "")).strip()
        if class_name and root:
            return f"{class_name}:{root}"
        return class_name or root or "node"
    if kind == "raw_token":
        return str(value.get("value", ""))
    if kind == "typed_literal":
        class_name = str(value.get("class_name", "")).strip()
        root = str(value.get("root", "")).strip()
        literal = value.get("value")
        label = f"{class_name}:{root}".strip(":")
        return f"{label}={literal}" if literal is not None else label
    if kind == "list":
        return [_ast_value_label(item) for item in value.get("items", [])]
    return str(value)


def _ast_roles_to_inputs(roles):
    role_map = {}
    for role in roles if isinstance(roles, list) else []:
        if not isinstance(role, dict):
            continue
        name = str(role.get("name", "")).strip()
        if not name:
            continue
        role_map[name] = _ast_value_label(role.get("value"))
    return role_map


def _safe_ast_action_type(class_name, root):
    if class_name == "EXEC":
        return SAFE_EXEC_ROOT_ACTION_TYPES.get(root, "inspect")
    return "inspect"


def _normalize_ast_document(ast_document):
    ast_node = ast_document.get("ast")
    if not isinstance(ast_node, dict):
        return None

    class_name = str(ast_node.get("class_name", "")).strip() or "AST"
    root = str(ast_node.get("root", "")).strip() or "UNKNOWN"
    source_profile = str(ast_document.get("source_profile", "")).strip() or "core"
    source_text = str(ast_document.get("source_text", "")).strip()
    schema_version = str(ast_document.get("schema_version", "")).strip()
    roles = _ast_roles_to_inputs(ast_node.get("roles", []))
    modifiers = list(ast_node.get("modifiers", [])) if isinstance(ast_node.get("modifiers"), list) else []

    return {
        "version": "0.1",
        "source": {
            "system": "SEMASCRIPT",
            "document_id": str(ast_document.get("document_id", "")).strip()
            or str((ast_document.get("metadata") or {}).get("document_id", "")).strip()
            or "semascript-ast-sample",
            "source_profile": source_profile,
        },
        "intent": {
            "summary": f"Normalize SEMASCRIPT {class_name}:{root} AST for dry-run preview",
            "objective": "Verify read-only AST compatibility without enabling execution.",
        },
        "actions": [
            {
                "id": "ast-root-1",
                "type": _safe_ast_action_type(class_name, root),
                "description": f"Preview SEMASCRIPT {class_name}:{root} AST node",
                "inputs": {
                    "ast_class": class_name,
                    "ast_root": root,
                    "modifiers": modifiers,
                    "roles": roles,
                },
                "expected_output": "Dry-run planner preview only",
            }
        ],
        "constraints": {
            "no_execution": True,
            "source_profile": source_profile,
            "source_text_present": bool(source_text),
        },
        "safety": {
            "dry_run_only": True,
            "requires_approval": True,
            "forbidden_operations": [
                "execute",
                "mutate_gptmeai_storage",
                "mutate_gptmeai_memory",
                "mutate_semascript_runtime",
            ],
        },
        "metadata": {
            "normalized_from": "semascript_ast",
            "schema_version": schema_version,
            "source_text": source_text,
            "validation_annotations": list(ast_document.get("validation_annotations", [])),
        },
    }


def normalize_semascript_ast(ast_document):
    if not isinstance(ast_document, dict):
        raise TypeError("ast_document must be an object")

    if REQUIRED_FIELDS.issubset(ast_document.keys()):
        return dict(ast_document)

    ast_normalized = _normalize_ast_document(ast_document)
    if ast_normalized is not None:
        return ast_normalized

    safety = dict(ast_document.get("safety") or {})
    safety["dry_run_only"] = True
    safety["requires_approval"] = True

    metadata = dict(ast_document.get("metadata") or {})
    metadata.setdefault("normalized_from", "semascript_ast")

    return {
        "version": str(ast_document.get("version", "0.1")),
        "source": _normalize_source(ast_document.get("source")),
        "intent": _normalize_intent(ast_document.get("intent"), ast_document),
        "actions": _normalize_actions(ast_document.get("actions") or ast_document.get("steps")),
        "constraints": dict(ast_document.get("constraints") or {}),
        "safety": safety,
        "metadata": metadata,
    }
