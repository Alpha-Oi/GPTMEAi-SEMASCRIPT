import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path

from drift_response import DriftResponseEngine
from execution_enforcement import ExecutionEnforcementEngine
from live_sync import LiveSyncEngine


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_INDEX = ROOT / "reports" / "codex" / "ARTIFACT_INDEX.json"
RUNTIME_ROOT = ROOT / "gptmeai-semascript"


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_fingerprint(root):
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        files.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    payload = json.dumps(files, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ControlledLiveSyncEngine(LiveSyncEngine):
    """Test-local LiveSyncEngine with deterministic injected runtime state."""

    def __init__(self, artifact_index_path, runtime_root, mode):
        super().__init__(artifact_index_path, runtime_root)
        self.mode = mode

    def poll_runtime_state(self):
        artifact_state = self.fetch_artifact_state()
        runtime_state = {
            "runtime_path": "gptmeai-semascript/",
            "observed_modules": list(artifact_state["expected_modules"]),
            "observed_flow": list(artifact_state["expected_flow"]),
            "runtime_event_ids": list(artifact_state["artifact_event_ids"]),
            "governance_markers": {
                "risk_before_governance": True,
                "governance_before_validation": True,
                "validation_before_execution": True,
                "execution_boundary_present": True,
            },
            "lineage_chain": list(artifact_state["lineage_chain"]),
            "runtime_executed": False,
            "observation_mode": f"test_fixture_{self.mode}",
        }

        if self.mode == "critical_drift":
            runtime_state["observed_modules"] = [
                module
                for module in runtime_state["observed_modules"]
                if module != "core.validation_engine"
            ]
            first_event = runtime_state["runtime_event_ids"][0]
            runtime_state["runtime_event_ids"] = [first_event, first_event]

        return runtime_state


def normalize_enforcement_status(status):
    if status == "BLOCKED":
        return "BLOCKED"
    return "ENFORCED"


def run_pipeline(mode):
    live_sync = ControlledLiveSyncEngine(
        artifact_index_path=ARTIFACT_INDEX,
        runtime_root=RUNTIME_ROOT,
        mode=mode,
    )
    drift_report = live_sync.synchronize()
    drift_event = live_sync.emit_sync_event(drift_report)

    response_engine = DriftResponseEngine()
    drift_response = response_engine.evaluate_drift(drift_report)
    response_event = response_engine.emit_response_event(
        drift_response,
        drift_report_id=f"drift-report::{mode}",
    )

    risk = {
        "risk_level": "LOW",
        "score": 10,
    }
    governance_approval = {
        "approved": drift_response["response_type"] not in {"BLOCK_EXECUTION"},
        "decision": "APPROVED"
        if drift_response["response_type"] not in {"BLOCK_EXECUTION"}
        else "BLOCKED",
        "approved_by": "governed-lifecycle-smoke",
    }

    enforcement = ExecutionEnforcementEngine().evaluate_response(
        response_event,
        governance_approval=governance_approval,
        risk_result=risk,
    )

    return {
        "drift_status": drift_report["drift_status"],
        "response_status": drift_response["response_type"],
        "enforcement_status": normalize_enforcement_status(enforcement["execution_status"]),
        "events_emitted": [
            deepcopy(drift_event),
            deepcopy(response_event),
            deepcopy(enforcement["event"]),
        ],
        "mutation_occurred": False,
        "details": {
            "drift_level": drift_report["drift_level"],
            "drift_types": list(drift_report["drift_types"]),
            "execution_status": enforcement["execution_status"],
            "runtime_mutation": enforcement["runtime_mutation"],
            "external_execution": enforcement["external_execution"],
            "runtime_observation": deepcopy(drift_report["runtime_observation"]),
        },
    }


class GovernedLifecycleSmokeTests(unittest.TestCase):
    def assert_output_shape(self, result):
        self.assertIn(result["drift_status"], {"NO_DRIFT", "DRIFT_DETECTED"})
        self.assertIn(result["response_status"], {"NO_ACTION", "BLOCK_EXECUTION"})
        self.assertIn(result["enforcement_status"], {"ENFORCED", "BLOCKED"})
        self.assertIsInstance(result["events_emitted"], list)
        self.assertFalse(result["mutation_occurred"])

    def test_no_drift_path_is_audit_only_and_non_mutating(self):
        before_index = file_hash(ARTIFACT_INDEX)
        before_runtime = tree_fingerprint(RUNTIME_ROOT)

        result = run_pipeline("no_drift")

        self.assert_output_shape(result)
        self.assertEqual("NO_DRIFT", result["drift_status"])
        self.assertEqual("NO_ACTION", result["response_status"])
        self.assertEqual("ENFORCED", result["enforcement_status"])
        self.assertEqual("SYNC_OK", result["events_emitted"][0]["event_type"])
        self.assertEqual("DRIFT_RESPONSE_GENERATED", result["events_emitted"][1]["event_type"])
        self.assertEqual("EXECUTION_ENFORCED", result["events_emitted"][2]["event_type"])
        self.assertFalse(result["details"]["runtime_observation"]["runtime_executed"])
        self.assertFalse(result["details"]["runtime_mutation"])
        self.assertFalse(result["details"]["external_execution"])
        self.assertEqual(before_index, file_hash(ARTIFACT_INDEX))
        self.assertEqual(before_runtime, tree_fingerprint(RUNTIME_ROOT))

    def test_critical_drift_path_blocks_enforcement_without_mutation(self):
        before_index = file_hash(ARTIFACT_INDEX)
        before_runtime = tree_fingerprint(RUNTIME_ROOT)

        result = run_pipeline("critical_drift")

        self.assert_output_shape(result)
        self.assertEqual("DRIFT_DETECTED", result["drift_status"])
        self.assertEqual("CRITICAL", result["details"]["drift_level"])
        self.assertIn("STRUCTURAL_DRIFT", result["details"]["drift_types"])
        self.assertIn("EVENT_DRIFT", result["details"]["drift_types"])
        self.assertEqual("BLOCK_EXECUTION", result["response_status"])
        self.assertEqual("BLOCKED", result["enforcement_status"])
        self.assertEqual("DRIFT_DETECTED", result["events_emitted"][0]["event_type"])
        self.assertEqual("EXECUTION_ENFORCED", result["events_emitted"][2]["event_type"])
        self.assertFalse(result["details"]["runtime_mutation"])
        self.assertFalse(result["details"]["external_execution"])
        self.assertEqual(before_index, file_hash(ARTIFACT_INDEX))
        self.assertEqual(before_runtime, tree_fingerprint(RUNTIME_ROOT))

    def test_pipeline_is_deterministic_for_identical_input(self):
        self.assertEqual(run_pipeline("no_drift"), run_pipeline("no_drift"))
        self.assertEqual(run_pipeline("critical_drift"), run_pipeline("critical_drift"))

    def test_artifact_index_and_runtime_are_immutable_across_pipeline(self):
        before_index = file_hash(ARTIFACT_INDEX)
        before_runtime = tree_fingerprint(RUNTIME_ROOT)

        _ = run_pipeline("no_drift")
        _ = run_pipeline("critical_drift")

        self.assertEqual(before_index, file_hash(ARTIFACT_INDEX))
        self.assertEqual(before_runtime, tree_fingerprint(RUNTIME_ROOT))


if __name__ == "__main__":
    unittest.main()
