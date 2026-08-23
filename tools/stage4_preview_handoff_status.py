"""Print a local read-only Stage 4 preview-handoff status summary."""

import copy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.stage4_preview_handoff_adapter import (  # noqa: E402
    build_stage4_preview_handoff_from_documents,
)
from tools.stage4_preview_handoff_builder import (  # noqa: E402
    assert_stage4_preview_handoff_envelope_valid,
)


ACTION_DOCUMENT = {
    "version": "0.1",
    "source": {
        "system": "SEMASCRIPT",
        "document_id": "sem-status-001",
    },
    "intent": {
        "summary": "Build a local Stage 4 preview-handoff status envelope",
    },
    "actions": [
        {
            "id": "action-1",
            "type": "inspect",
            "description": "Inspect local Stage 4 preview-handoff status",
            "inputs": {"target": "stage4-preview-handoff"},
            "expected_output": "status-summary",
        }
    ],
    "constraints": {
        "dry_run": True,
    },
    "safety": {
        "dry_run_only": True,
        "requires_approval": True,
        "forbidden_operations": [
            "execute",
            "dispatch",
            "runtime_call",
            "storage_mutation",
        ],
    },
    "metadata": {
        "fixture": "stage4-preview-handoff-status-cli",
    },
}

PLANNER_PREVIEW = {
    "version": "0.1",
    "preview_id": "preview-status-001",
    "status": "preview",
    "mapped_actions": [
        {
            "source_action_id": "action-1",
            "operation": "inspect",
            "planner_step": "Inspect local Stage 4 preview-handoff status",
        }
    ],
    "required_approvals": [
        {
            "type": "execution_approval",
            "required": True,
        }
    ],
    "risks": [
        {
            "level": "low",
            "message": "dry-run preview status only",
        }
    ],
    "dry_run": True,
    "metadata": {
        "source_system": "SEMASCRIPT",
        "fixture_source": "embedded",
    },
}

SOURCE_EVIDENCE = {
    "fixture_source": "embedded",
    "files": [
        "tools/stage4_preview_handoff_adapter.py",
        "tools/stage4_preview_handoff_builder.py",
        "tools/stage4_preview_handoff_contract.py",
    ],
}


def build_status_envelope():
    """Build and validate the embedded local preview-handoff status envelope."""
    envelope = build_stage4_preview_handoff_from_documents(
        copy.deepcopy(ACTION_DOCUMENT),
        copy.deepcopy(PLANNER_PREVIEW),
        source_evidence=copy.deepcopy(SOURCE_EVIDENCE),
    )
    assert_stage4_preview_handoff_envelope_valid(envelope)
    return envelope


def status_lines(envelope):
    """Return deterministic status lines for smoke/status use."""
    mode_flags = envelope["mode_flags"]
    approval_gate = envelope["approval_gate"]
    return [
        "STAGE4_PREVIEW_HANDOFF_STATUS=OK",
        f"HANDOFF_TYPE={envelope['handoff_type']}",
        f"ENVELOPE_ID={envelope['envelope_id']}",
        f"DRY_RUN={mode_flags['dry_run']}",
        f"PREVIEW_ONLY={mode_flags['preview_only']}",
        f"EXECUTION_ALLOWED={mode_flags['execution_allowed']}",
        f"MUTATION_ALLOWED={mode_flags['mutation_allowed']}",
        f"REQUIRES_HUMAN_APPROVAL={mode_flags['requires_human_approval']}",
        f"APPROVAL_GATE={approval_gate['status']}",
        "RUNTIME_CALLS=none",
        "SOURCE_PROJECT_MUTATION=none",
        "FIXTURE_SOURCE=embedded",
    ]


def main(argv=None):
    _ = argv
    try:
        envelope = build_status_envelope()
    except Exception as exc:
        print("STAGE4_PREVIEW_HANDOFF_STATUS=FAIL")
        print(f"ERROR={exc}")
        return 1

    for line in status_lines(envelope):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
