"""Build local dry-run Stage 4 preview-handoff envelopes."""

import copy
import hashlib
import json

from tools.stage4_preview_handoff_contract import (
    REQUIRED_MUTATION_BOUNDARIES,
    REQUIRED_NON_GOALS,
    assert_stage4_preview_handoff_contract_valid,
    load_stage4_preview_handoff_contract,
)


HANDOFF_TYPE = "STAGE4_PREVIEW_HANDOFF"

REQUIRED_ENVELOPE_SECTIONS = (
    "envelope_id",
    "handoff_type",
    "contract",
    "mode_flags",
    "semascript_action_document",
    "normalized_action_document",
    "gptmeai_planner_preview",
    "planner_preview_handoff",
    "diagnostics",
    "source_evidence",
    "approval_gate",
    "stopped_at",
    "mutation_boundaries",
    "explicit_non_goals",
)

EXPECTED_MODE_FLAGS = {
    "dry_run": True,
    "preview_only": True,
    "execution_allowed": False,
    "mutation_allowed": False,
    "requires_human_approval": True,
}

FORBIDDEN_TOP_LEVEL_RESULTS = {
    "execution_result",
    "dispatch_result",
    "runtime_mutation_result",
}

FORBIDDEN_TRUE_MARKERS = (
    '"execute": true',
    '"execution_allowed": true',
    '"mutation_allowed": true',
    '"dispatch_allowed": true',
    '"runtime_call_allowed": true',
    '"planner_execution": true',
    '"runtime_mutation": true',
    '"storage_mutation": true',
    '"memory_mutation": true',
    '"ledger_mutation": true',
    '"session_mutation": true',
    '"workspace_mutation": true',
    '"lineage_mutation": true',
)


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _json_hash(payload):
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _contract_summary(contract):
    return {
        "contract_id": contract.get("contract_id"),
        "version": contract.get("version"),
        "status": contract.get("status"),
    }


def _normalized_action_document(action_document):
    return {
        "version": action_document.get("version"),
        "source": copy.deepcopy(action_document.get("source", {})),
        "intent": copy.deepcopy(action_document.get("intent", {})),
        "actions": copy.deepcopy(action_document.get("actions", [])),
        "constraints": copy.deepcopy(action_document.get("constraints", {})),
        "safety": copy.deepcopy(action_document.get("safety", {})),
        "metadata": {
            "normalized_from": "semascript_action_document",
            "source_metadata": copy.deepcopy(action_document.get("metadata", {})),
        },
    }


def _planner_preview_handoff(planner_preview):
    return {
        "preview_id": planner_preview.get("preview_id"),
        "status": planner_preview.get("status"),
        "mapped_actions": copy.deepcopy(planner_preview.get("mapped_actions", [])),
        "required_approvals": copy.deepcopy(
            planner_preview.get("required_approvals", [])
        ),
        "risks": copy.deepcopy(planner_preview.get("risks", [])),
        "dry_run": planner_preview.get("dry_run") is True,
        "execution_allowed": False,
        "dispatch_allowed": False,
        "runtime_call_allowed": False,
        "contract_ref": "contracts/gptmeai_planner_preview.schema.json",
    }


def _envelope_id(action_document, planner_preview, source_evidence, contract):
    digest = _json_hash(
        {
            "handoff_type": HANDOFF_TYPE,
            "action_document": action_document,
            "planner_preview": planner_preview,
            "source_evidence": source_evidence,
            "contract": _contract_summary(contract),
        }
    )
    return f"stage4-preview-handoff-{digest[:16]}"


def build_stage4_preview_handoff(
    semascript_action_document,
    gptmeai_planner_preview,
    *,
    source_evidence=None,
    contract=None,
):
    """Build and validate a local dry-run Stage 4 preview-handoff envelope."""
    _require_dict(semascript_action_document, "semascript_action_document")
    _require_dict(gptmeai_planner_preview, "gptmeai_planner_preview")
    if source_evidence is not None:
        _require_dict(source_evidence, "source_evidence")

    active_contract = (
        load_stage4_preview_handoff_contract() if contract is None else contract
    )
    _require_dict(active_contract, "contract")
    assert_stage4_preview_handoff_contract_valid(active_contract)

    action_document = copy.deepcopy(semascript_action_document)
    planner_preview = copy.deepcopy(gptmeai_planner_preview)
    evidence = copy.deepcopy(source_evidence or {})

    envelope = {
        "envelope_id": _envelope_id(
            action_document,
            planner_preview,
            evidence,
            active_contract,
        ),
        "handoff_type": HANDOFF_TYPE,
        "contract": _contract_summary(active_contract),
        "mode_flags": copy.deepcopy(active_contract["mode_flags"]),
        "semascript_action_document": action_document,
        "normalized_action_document": _normalized_action_document(action_document),
        "gptmeai_planner_preview": planner_preview,
        "planner_preview_handoff": _planner_preview_handoff(planner_preview),
        "diagnostics": [
            {
                "level": "info",
                "message": "Built local dry-run preview handoff; no runtime calls performed.",
            }
        ],
        "source_evidence": evidence,
        "approval_gate": {
            "status": "required",
            "requires_human_approval": True,
            "approved": False,
            "execution_enabled": False,
            "scope": "preview-handoff-review-only",
        },
        "stopped_at": "approval_gate",
        "mutation_boundaries": copy.deepcopy(active_contract["mutation_boundaries"]),
        "explicit_non_goals": copy.deepcopy(active_contract["explicit_non_goals"]),
    }
    assert_stage4_preview_handoff_envelope_valid(envelope)
    return envelope


def validate_stage4_preview_handoff_envelope(envelope):
    """Return validation errors for a local Stage 4 preview-handoff envelope."""
    errors = []
    if not isinstance(envelope, dict):
        return ["envelope must be a dict"]

    for section in REQUIRED_ENVELOPE_SECTIONS:
        if section not in envelope:
            errors.append(f"missing required envelope section: {section}")

    if envelope.get("handoff_type") != HANDOFF_TYPE:
        errors.append(f"handoff_type must be {HANDOFF_TYPE}")

    if not str(envelope.get("envelope_id", "")).startswith("stage4-preview-handoff-"):
        errors.append("envelope_id must be a deterministic stage4-preview-handoff id")

    contract = envelope.get("contract")
    if not isinstance(contract, dict):
        errors.append("contract must be an object")
    else:
        if contract.get("contract_id") != HANDOFF_TYPE:
            errors.append(f"contract.contract_id must be {HANDOFF_TYPE}")
        if not str(contract.get("version", "")).strip():
            errors.append("contract.version must be present")
        if "draft" not in str(contract.get("status", "")).lower():
            errors.append("contract.status must indicate draft")

    mode_flags = envelope.get("mode_flags")
    if not isinstance(mode_flags, dict):
        errors.append("mode_flags must be an object")
    else:
        for flag, expected in EXPECTED_MODE_FLAGS.items():
            if mode_flags.get(flag) is not expected:
                errors.append(f"mode_flags.{flag} must be {str(expected).lower()}")

    for key in (
        "semascript_action_document",
        "normalized_action_document",
        "gptmeai_planner_preview",
        "planner_preview_handoff",
        "source_evidence",
        "approval_gate",
    ):
        if key in envelope and not isinstance(envelope[key], dict):
            errors.append(f"{key} must be an object")

    if "diagnostics" in envelope and not isinstance(envelope["diagnostics"], list):
        errors.append("diagnostics must be a list")

    handoff = envelope.get("planner_preview_handoff", {})
    if isinstance(handoff, dict):
        if handoff.get("dry_run") is not True:
            errors.append("planner_preview_handoff.dry_run must be true")
        for flag in ("execution_allowed", "dispatch_allowed", "runtime_call_allowed"):
            if handoff.get(flag) is not False:
                errors.append(f"planner_preview_handoff.{flag} must be false")

    approval_gate = envelope.get("approval_gate", {})
    if isinstance(approval_gate, dict):
        if approval_gate.get("status") not in {"required", "pending"}:
            errors.append("approval_gate.status must be required or pending")
        if approval_gate.get("requires_human_approval") is not True:
            errors.append("approval_gate.requires_human_approval must be true")
        if approval_gate.get("approved") is not False:
            errors.append("approval_gate.approved must be false")
        if approval_gate.get("execution_enabled") is not False:
            errors.append("approval_gate.execution_enabled must be false")

    if envelope.get("stopped_at") != "approval_gate":
        errors.append("stopped_at must be approval_gate")

    for result_key in sorted(FORBIDDEN_TOP_LEVEL_RESULTS):
        if result_key in envelope:
            errors.append(f"forbidden runtime result key present: {result_key}")

    boundaries = set(envelope.get("mutation_boundaries", []))
    missing_boundaries = sorted(REQUIRED_MUTATION_BOUNDARIES - boundaries)
    if missing_boundaries:
        errors.append(
            "mutation_boundaries missing required entries: "
            + ", ".join(missing_boundaries)
        )

    non_goals = set(envelope.get("explicit_non_goals", []))
    missing_non_goals = sorted(REQUIRED_NON_GOALS - non_goals)
    if missing_non_goals:
        errors.append(
            "explicit_non_goals missing required entries: "
            + ", ".join(missing_non_goals)
        )

    serialized = json.dumps(envelope, sort_keys=True).lower()
    for marker in FORBIDDEN_TRUE_MARKERS:
        if marker in serialized:
            errors.append(f"forbidden true marker present: {marker}")

    return errors


def assert_stage4_preview_handoff_envelope_valid(envelope):
    """Raise ValueError if the Stage 4 preview-handoff envelope is invalid."""
    errors = validate_stage4_preview_handoff_envelope(envelope)
    if errors:
        raise ValueError(
            "Invalid Stage 4 preview-handoff envelope: " + "; ".join(errors)
        )
