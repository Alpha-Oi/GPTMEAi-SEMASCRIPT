import json
import tempfile
import unittest
from pathlib import Path

from live_sync import DriftDetector, LiveSyncEngine


ROOT = Path(__file__).resolve().parents[1]


class LiveSyncDriftDetectionTests(unittest.TestCase):
    def artifact_state(self):
        return {
            "artifact_id": "executable-bootstrap-codebase::1.0::2026-05-27",
            "expected_modules": [
                "core.event_store",
                "core.state_engine",
                "core.risk_engine",
                "core.governance",
                "core.validation_engine",
                "core.execution_boundary",
                "runtime.orchestrator",
                "runtime.loop_runner",
                "bridge.semascript_bridge",
            ],
            "expected_flow": [
                "event_store",
                "state_engine",
                "snapshot",
                "mental_model",
                "risk_engine",
                "governance_engine",
                "validation_engine",
                "execution_boundary",
                "event_store_append",
            ],
            "artifact_event_ids": [
                "event::2026-05-27::codebase-skeleton::artifact-created::001",
                "event::2026-05-27::executable-bootstrap-codebase::artifact-created::001",
            ],
            "lineage_chain": [
                "system-map::2.0::2026-05-27",
                "validation-checklist-layer::1.0::2026-05-27",
                "system-engineering-blueprint-mode::1.0::2026-05-27",
                "codebase-skeleton::1.0::2026-05-27",
                "executable-bootstrap-codebase::1.0::2026-05-27",
            ],
        }

    def runtime_state(self):
        state = self.artifact_state()
        return {
            "runtime_path": "gptmeai-semascript/",
            "observed_modules": list(state["expected_modules"]),
            "observed_flow": list(state["expected_flow"]),
            "runtime_event_ids": list(state["artifact_event_ids"]),
            "governance_markers": {
                "risk_before_governance": True,
                "governance_before_validation": True,
                "validation_before_execution": True,
                "execution_boundary_present": True,
            },
            "lineage_chain": list(state["lineage_chain"]),
        }

    def test_no_drift_report_is_stable(self):
        detector = DriftDetector()

        first = detector.compare_artifact_vs_runtime(self.artifact_state(), self.runtime_state())
        second = detector.compare_artifact_vs_runtime(self.artifact_state(), self.runtime_state())

        self.assertEqual(first, second)
        self.assertEqual("NO_DRIFT", first["drift_status"])
        self.assertEqual([], first["drift_types"])

    def test_structural_mismatch_detection(self):
        runtime = self.runtime_state()
        runtime["observed_modules"].remove("core.validation_engine")

        report = DriftDetector().compare_artifact_vs_runtime(self.artifact_state(), runtime)

        self.assertEqual("DRIFT_DETECTED", report["drift_status"])
        self.assertIn("STRUCTURAL_DRIFT", report["drift_types"])
        self.assertIn("core.validation_engine", report["details"]["structural"]["missing_modules"])

    def test_event_mismatch_detection(self):
        runtime = self.runtime_state()
        runtime["runtime_event_ids"] = [runtime["runtime_event_ids"][0], runtime["runtime_event_ids"][0]]

        report = DriftDetector().compare_artifact_vs_runtime(self.artifact_state(), runtime)

        self.assertIn("EVENT_DRIFT", report["drift_types"])
        self.assertIn(
            runtime["runtime_event_ids"][0],
            report["details"]["event"]["duplicated_runtime_events"],
        )

    def test_governance_bypass_detection(self):
        runtime = self.runtime_state()
        runtime["governance_markers"]["risk_before_governance"] = False

        report = DriftDetector().compare_artifact_vs_runtime(self.artifact_state(), runtime)

        self.assertIn("GOVERNANCE_DRIFT", report["drift_types"])
        self.assertTrue(report["requires_governance_review"])

    def test_lineage_mismatch_detection(self):
        runtime = self.runtime_state()
        runtime["lineage_chain"] = runtime["lineage_chain"][:-1]

        report = DriftDetector().compare_artifact_vs_runtime(self.artifact_state(), runtime)

        self.assertIn("LINEAGE_DRIFT", report["drift_types"])
        self.assertEqual("HIGH", report["drift_level"])

    def test_live_sync_reads_runtime_without_executing_it(self):
        engine = LiveSyncEngine(
            artifact_index_path=ROOT / "reports" / "codex" / "ARTIFACT_INDEX.json",
            runtime_root=ROOT / "gptmeai-semascript",
        )

        report = engine.synchronize()
        event = engine.emit_sync_event(report)

        self.assertIn(report["drift_status"], {"NO_DRIFT", "DRIFT_DETECTED"})
        self.assertIn(event["event_type"], {"SYNC_OK", "DRIFT_DETECTED"})
        self.assertFalse(report["runtime_observation"]["runtime_executed"])

    def test_live_sync_event_schema_is_valid_json(self):
        schema_path = ROOT / "contracts" / "live_sync_drift_event.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertEqual("object", schema["type"])
        self.assertIn("event_type", schema["required"])
        self.assertIn("payload", schema["required"])


if __name__ == "__main__":
    unittest.main()
