"""Compose validated in-memory documents into a Stage 4 preview handoff."""

import copy

from bridge.semascript_validator import validate_action_document
from tools.stage4_preview_handoff_builder import build_stage4_preview_handoff
from tools.stage4_preview_handoff_contract import (
    assert_stage4_preview_handoff_contract_valid,
    load_stage4_preview_handoff_contract,
)


REQUIRED_PLANNER_PREVIEW_FIELDS = (
    "version",
    "preview_id",
    "status",
    "mapped_actions",
    "required_approvals",
    "risks",
    "dry_run",
    "metadata",
)

PLANNER_PREVIEW_LIST_FIELDS = (
    "mapped_actions",
    "required_approvals",
    "risks",
)

ADAPTER_SOURCE_EVIDENCE = {
    "semascript_validator": "bridge.semascript_validator.validate_action_document",
    "planner_preview_validation": "local_adapter_required_field_check",
    "stage4_contract_validator": (
        "tools.stage4_preview_handoff_contract."
        "assert_stage4_preview_handoff_contract_valid"
    ),
    "stage4_builder": "tools.stage4_preview_handoff_builder.build_stage4_preview_handoff",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        return [f"{name} must be a dict"]
    return []


def _format_semascript_validation_errors(validation):
    errors = []
    for item in validation.get("errors", []):
        field = str(item.get("field", "$"))
        message = str(item.get("message", "invalid"))
        if field == "$":
            errors.append(f"semascript_action_document: {message}")
        else:
            errors.append(f"semascript_action_document.{field}: {message}")
    return errors


def _validate_planner_preview(planner_preview):
    errors = []

    for field in REQUIRED_PLANNER_PREVIEW_FIELDS:
        if field not in planner_preview:
            errors.append(f"gptmeai_planner_preview.{field}: missing required field")

    for field in ("version", "preview_id"):
        if field in planner_preview and not isinstance(planner_preview[field], str):
            errors.append(f"gptmeai_planner_preview.{field}: expected string")

    if planner_preview.get("status") not in {"preview", "rejected"}:
        errors.append("gptmeai_planner_preview.status: expected preview or rejected")

    for field in PLANNER_PREVIEW_LIST_FIELDS:
        if field in planner_preview and not isinstance(planner_preview[field], list):
            errors.append(f"gptmeai_planner_preview.{field}: expected list")

    if "dry_run" in planner_preview and planner_preview.get("dry_run") is not True:
        errors.append("gptmeai_planner_preview.dry_run: expected true")

    if "metadata" in planner_preview and not isinstance(planner_preview["metadata"], dict):
        errors.append("gptmeai_planner_preview.metadata: expected dict")

    return errors


def validate_stage4_preview_handoff_adapter_inputs(
    semascript_action_document,
    gptmeai_planner_preview,
    *,
    source_evidence=None,
):
    """Return adapter input validation errors without mutating caller data."""
    errors = []
    errors.extend(_require_dict(semascript_action_document, "semascript_action_document"))
    errors.extend(_require_dict(gptmeai_planner_preview, "gptmeai_planner_preview"))
    if source_evidence is not None:
        errors.extend(_require_dict(source_evidence, "source_evidence"))
    if errors:
        return errors

    validation = validate_action_document(copy.deepcopy(semascript_action_document))
    if not validation.get("valid"):
        errors.extend(_format_semascript_validation_errors(validation))

    errors.extend(_validate_planner_preview(copy.deepcopy(gptmeai_planner_preview)))
    return errors


def _source_evidence_with_adapter_details(source_evidence):
    evidence = copy.deepcopy(source_evidence or {})
    evidence["adapter"] = copy.deepcopy(ADAPTER_SOURCE_EVIDENCE)
    return evidence


def build_stage4_preview_handoff_from_documents(
    semascript_action_document,
    gptmeai_planner_preview,
    *,
    source_evidence=None,
    contract=None,
):
    """Return a local dry-run Stage 4 preview-handoff envelope only."""
    errors = validate_stage4_preview_handoff_adapter_inputs(
        semascript_action_document,
        gptmeai_planner_preview,
        source_evidence=source_evidence,
    )
    if errors:
        raise ValueError(
            "Invalid Stage 4 preview-handoff adapter inputs: " + "; ".join(errors)
        )

    active_contract = (
        load_stage4_preview_handoff_contract() if contract is None else contract
    )
    assert_stage4_preview_handoff_contract_valid(active_contract)

    envelope = build_stage4_preview_handoff(
        copy.deepcopy(semascript_action_document),
        copy.deepcopy(gptmeai_planner_preview),
        source_evidence=_source_evidence_with_adapter_details(source_evidence),
        contract=active_contract,
    )
    envelope["diagnostics"] = copy.deepcopy(envelope["diagnostics"])
    envelope["diagnostics"].append(
        {
            "level": "info",
            "message": (
                "Adapter composed SEMASCRIPT validation, Stage 4 contract "
                "validation, and local preview-handoff builder without runtime calls."
            ),
        }
    )
    return envelope
