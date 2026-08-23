"""SEMASCRIPT to GPTMEAi planner preview mapper."""

from datetime import datetime, timezone
from uuid import uuid4

from .config import DRY_RUN, REQUIRE_APPROVAL
from .semascript_validator import validate_action_document

RISKY_ACTION_TYPES = {"execute", "shell", "write", "delete", "mutate", "network"}


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _map_action(action):
    return {
        "source_action_id": action["id"],
        "operation": action["type"],
        "planner_step": action["description"],
        "inputs": action.get("inputs", {}),
        "expected_output": action.get("expected_output", ""),
        "execution_mode": "dry_run",
    }


def _build_risks(actions):
    risks = [
        {
            "level": "low",
            "description": "v0.1 creates a planner preview only; GPTMEAi execution is not called.",
        }
    ]
    risky_actions = [
        action
        for action in actions
        if str(action.get("type", "")).strip().lower() in RISKY_ACTION_TYPES
    ]
    if risky_actions:
        risks.append(
            {
                "level": "medium",
                "description": "Action types include operations that must remain blocked until explicit approval and a future execution-enabled release.",
                "action_ids": [action.get("id", "") for action in risky_actions],
            }
        )
    return risks


def map_semascript_to_planner_preview(action_document):
    """Map a validated SEMASCRIPT action document into a dry-run preview."""
    validation = validate_action_document(action_document)
    if not validation["valid"]:
        messages = "; ".join(error["message"] for error in validation["errors"])
        raise ValueError(f"Invalid SEMASCRIPT action document: {messages}")

    actions = action_document["actions"]
    source = action_document.get("source", {})
    intent = action_document.get("intent", {})

    return {
        "version": "0.1",
        "preview_id": f"preview-{uuid4()}",
        "status": "preview",
        "mapped_actions": [_map_action(action) for action in actions],
        "required_approvals": [
            {
                "type": "execution_approval",
                "required": True,
                "reason": "All GPTMEAi execution remains blocked behind an approval gate in v0.1.",
            }
        ],
        "risks": _build_risks(actions),
        "dry_run": True,
        "metadata": {
            "adapter": "GPTMEAi-SEMASCRIPT",
            "created_at": _utc_now(),
            "source_system": source.get("system", "SEMASCRIPT"),
            "source_document_id": source.get("document_id", ""),
            "intent_summary": intent.get("summary", ""),
            "action_count": len(actions),
            "config_dry_run": DRY_RUN,
            "config_requires_approval": REQUIRE_APPROVAL,
            "validation_warnings": validation["warnings"],
        },
    }
