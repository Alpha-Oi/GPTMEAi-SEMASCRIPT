"""Read-only loader and validator for the Stage 4 preview-handoff contract."""

import json
from pathlib import Path
import sys


CONTRACT_ID = "STAGE4_PREVIEW_HANDOFF"
CONTRACT_FILENAME = "stage4_preview_handoff_contract.v0.1.json"

REQUIRED_SECTIONS = (
    "input_boundary",
    "output_boundary",
    "validation_stages",
    "mutation_boundaries",
    "explicit_non_goals",
    "required_source_evidence",
    "approval_gates",
    "rollback_plan",
    "verification_gates",
)

EXPECTED_MODE_FLAGS = {
    "dry_run": True,
    "preview_only": True,
    "execution_allowed": False,
    "mutation_allowed": False,
    "requires_human_approval": True,
}

REQUIRED_STAGE_IDS = (
    "validate_semascript_action_document",
    "normalize_action_document",
    "build_planner_preview_handoff",
    "stop_at_approval_gate",
)

REQUIRED_NON_GOALS = {
    "no execute method",
    "no dispatch",
    "no live runtime startup",
    "no planner execution",
    "no api runtime behavior change",
    "no schema data migration",
    "no dependency work",
}

REQUIRED_MUTATION_BOUNDARIES = {
    "no GPTMEAi source mutation",
    "no SEMASCRIPT source mutation",
    "no runtime mutation",
    "no storage mutation",
    "no memory mutation",
    "no session mutation",
    "no workspace mutation",
    "no lineage mutation",
    "no ledger mutation",
}

FORBIDDEN_TRUE_MARKERS = (
    '"execute": true',
    '"planner_execution": true',
    '"runtime_mutation": true',
    '"storage_mutation": true',
    '"memory_mutation": true',
    '"ledger_mutation": true',
    '"session_mutation": true',
    '"workspace_mutation": true',
    '"lineage_mutation": true',
)


def project_root():
    return Path(__file__).resolve().parents[1]


def default_contract_path():
    return project_root() / "contracts" / CONTRACT_FILENAME


def load_stage4_preview_handoff_contract(path=None):
    """Load the Stage 4 preview-handoff contract as a JSON object."""
    contract_path = default_contract_path() if path is None else Path(path)
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Stage 4 preview-handoff contract not found: {contract_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid Stage 4 preview-handoff contract JSON in {contract_path}: {exc}"
        ) from exc

    if not isinstance(contract, dict):
        raise ValueError("Stage 4 preview-handoff contract must be a JSON object")
    return contract


def _list_values(value):
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _section_type_errors(contract):
    expected_types = {
        "input_boundary": dict,
        "output_boundary": dict,
        "validation_stages": list,
        "mutation_boundaries": list,
        "explicit_non_goals": list,
        "required_source_evidence": list,
        "approval_gates": dict,
        "rollback_plan": dict,
        "verification_gates": list,
    }
    errors = []
    for section, expected_type in expected_types.items():
        if section not in contract:
            continue
        if not isinstance(contract[section], expected_type):
            errors.append(f"{section} must be a {expected_type.__name__}")
    return errors


def _stage_ids(contract):
    stages = contract.get("validation_stages", [])
    if not isinstance(stages, list):
        return []
    return [
        str(stage.get("id", ""))
        for stage in stages
        if isinstance(stage, dict) and str(stage.get("id", "")).strip()
    ]


def validate_stage4_preview_handoff_contract(contract):
    """Return a list of validation errors for a Stage 4 preview-handoff contract."""
    errors = []
    if not isinstance(contract, dict):
        return ["contract must be a JSON object"]

    if contract.get("contract_id") != CONTRACT_ID:
        errors.append(f"contract_id must be {CONTRACT_ID}")

    if not str(contract.get("version", "")).strip():
        errors.append("version must be present")

    status = str(contract.get("status", "")).lower()
    if "draft" not in status or "design" not in status:
        errors.append("status must indicate draft/design-only")

    mode_flags = contract.get("mode_flags")
    if not isinstance(mode_flags, dict):
        errors.append("mode_flags must be an object")
    else:
        for flag, expected in EXPECTED_MODE_FLAGS.items():
            if mode_flags.get(flag) is not expected:
                errors.append(f"mode_flags.{flag} must be {str(expected).lower()}")

    for section in REQUIRED_SECTIONS:
        if section not in contract:
            errors.append(f"missing required section: {section}")
    errors.extend(_section_type_errors(contract))

    stage_ids = _stage_ids(contract)
    if stage_ids != list(REQUIRED_STAGE_IDS):
        errors.append(
            "validation_stages must be ordered as: "
            + ", ".join(REQUIRED_STAGE_IDS)
        )

    stages = contract.get("validation_stages", [])
    if isinstance(stages, list):
        for stage in stages:
            if isinstance(stage, dict) and stage.get("mutation_allowed") is not False:
                errors.append(
                    "validation_stages entries must set mutation_allowed false"
                )

    non_goals = set(_list_values(contract.get("explicit_non_goals")))
    missing_non_goals = sorted(REQUIRED_NON_GOALS - non_goals)
    if missing_non_goals:
        errors.append(
            "explicit_non_goals missing required entries: "
            + ", ".join(missing_non_goals)
        )

    mutation_boundaries = set(_list_values(contract.get("mutation_boundaries")))
    missing_boundaries = sorted(REQUIRED_MUTATION_BOUNDARIES - mutation_boundaries)
    if missing_boundaries:
        errors.append(
            "mutation_boundaries missing required entries: "
            + ", ".join(missing_boundaries)
        )

    approval_gates = contract.get("approval_gates", {})
    if isinstance(approval_gates, dict):
        if approval_gates.get("human_approval_required") is not True:
            errors.append("approval_gates.human_approval_required must be true")

    output_boundary = contract.get("output_boundary", {})
    if isinstance(output_boundary, dict):
        approval_result = output_boundary.get("approval_gate_result", {})
        if isinstance(approval_result, dict):
            if approval_result.get("enables_execution") is not False:
                errors.append(
                    "output_boundary.approval_gate_result.enables_execution must be false"
                )

    serialized = json.dumps(contract, sort_keys=True).lower()
    for marker in FORBIDDEN_TRUE_MARKERS:
        if marker in serialized:
            errors.append(f"forbidden true marker present: {marker}")

    return errors


def assert_stage4_preview_handoff_contract_valid(contract):
    """Raise ValueError if the Stage 4 preview-handoff contract is invalid."""
    errors = validate_stage4_preview_handoff_contract(contract)
    if errors:
        raise ValueError(
            "Invalid Stage 4 preview-handoff contract: " + "; ".join(errors)
        )


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(args[0]) if args else None
    try:
        contract = load_stage4_preview_handoff_contract(path)
    except (FileNotFoundError, ValueError) as exc:
        print("STAGE4_PREVIEW_HANDOFF_CONTRACT=FAIL")
        print(str(exc))
        return 1

    errors = validate_stage4_preview_handoff_contract(contract)
    if errors:
        print("STAGE4_PREVIEW_HANDOFF_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("STAGE4_PREVIEW_HANDOFF_CONTRACT=OK")
    print(f"CONTRACT_ID={contract.get('contract_id')}")
    print(f"VERSION={contract.get('version')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
