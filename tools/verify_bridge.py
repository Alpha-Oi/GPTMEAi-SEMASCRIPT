"""Run local v0.1 bridge verification."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.approval_gate import require_approval
from bridge.config import GPTMEAI_BASE_URL
from bridge.gptmeai_client import GPTMEAiReadOnlyClient
from bridge.planner_preview_adapter import map_semascript_to_planner_preview
from bridge.semascript_validator import validate_action_document


def main():
    example_path = ROOT / "examples" / "semascript_action_document.example.json"
    document = json.loads(example_path.read_text(encoding="utf-8"))

    validation = validate_action_document(document)
    if not validation["valid"]:
        print("LOCAL_VALIDATION=FAILED")
        print(json.dumps(validation, indent=2))
        return 1
    print("LOCAL_VALIDATION=OK")

    preview = map_semascript_to_planner_preview(document)
    if preview.get("dry_run") is not True:
        print("DRY_RUN=FAILED")
        return 1
    print("DRY_RUN=OK")

    if not require_approval(preview):
        print("APPROVAL_GATE=FAILED")
        return 1
    print("APPROVAL_GATE=OK")

    client = GPTMEAiReadOnlyClient(GPTMEAI_BASE_URL, timeout=1.0)
    health = client.health()
    if health["available"]:
        print(f"GPTMEAI_HEALTH=AVAILABLE status_code={health['status_code']}")
    else:
        print(f"GPTMEAI_HEALTH=UNAVAILABLE error={health.get('error', '')}")

    print("VERIFY_BRIDGE=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
