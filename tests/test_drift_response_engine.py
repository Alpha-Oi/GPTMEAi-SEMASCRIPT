import json
import unittest
from pathlib import Path

from drift_response import DriftResponseEngine


ROOT = Path(__file__).resolve().parents[1]


class DriftResponseEngineTests(unittest.TestCase):
    def drift_report(self, level, drift_types):
        return {
            "drift_status": "DRIFT_DETECTED" if drift_types else "NO_DRIFT",
            "drift_level": level,
            "drift_types": list(drift_types),
            "affected_layers": ["governance"] if "GOVERNANCE_DRIFT" in drift_types else ["runtime_structure"],
            "recommended_action": "Open governance review before runtime or artifact changes.",
            "requires_governance_review": bool(drift_types),
            "artifact_state_id": "executable-bootstrap-codebase::1.0::2026-05-27",
        }

    def test_critical_drift_blocks_execution_first(self):
        response = DriftResponseEngine().evaluate_drift(
            self.drift_report("CRITICAL", ["STRUCTURAL_DRIFT", "EVENT_DRIFT"])
        )

        self.assertEqual("BLOCK_EXECUTION", response["response_type"])
        self.assertTrue(response["requires_governance_approval"])
        self.assertEqual("block_execution", response["staged_proposal"]["action"])
        self.assertFalse(response["staged_proposal"]["auto_apply"])

    def test_high_governance_or_event_drift_stages_rollback(self):
        response = DriftResponseEngine().evaluate_drift(
            self.drift_report("HIGH", ["GOVERNANCE_DRIFT"])
        )

        self.assertEqual("ROLLBACK", response["response_type"])
        self.assertTrue(response["requires_governance_approval"])
        self.assertEqual("stage_rollback", response["staged_proposal"]["action"])

    def test_high_structural_drift_stages_fix(self):
        response = DriftResponseEngine().evaluate_drift(
            self.drift_report("HIGH", ["STRUCTURAL_DRIFT"])
        )

        self.assertEqual("STAGE_FIX", response["response_type"])
        self.assertTrue(response["requires_governance_approval"])
        self.assertEqual("stage_fix", response["staged_proposal"]["action"])

    def test_medium_lineage_drift_revalidates(self):
        response = DriftResponseEngine().evaluate_drift(
            self.drift_report("MEDIUM", ["LINEAGE_DRIFT"])
        )

        self.assertEqual("REVALIDATE", response["response_type"])
        self.assertFalse(response["requires_governance_approval"])
        self.assertEqual("revalidate", response["staged_proposal"]["action"])

    def test_no_drift_requires_no_action(self):
        response = DriftResponseEngine().evaluate_drift(self.drift_report("LOW", []))

        self.assertEqual("NO_ACTION", response["response_type"])
        self.assertFalse(response["requires_governance_approval"])
        self.assertEqual({}, response["staged_proposal"])

    def test_response_is_deterministic(self):
        report = self.drift_report("HIGH", ["EVENT_DRIFT", "STRUCTURAL_DRIFT"])
        engine = DriftResponseEngine()

        self.assertEqual(engine.evaluate_drift(report), engine.evaluate_drift(report))

    def test_response_event_is_generated_without_applying_fix(self):
        engine = DriftResponseEngine()
        response = engine.evaluate_drift(self.drift_report("HIGH", ["STRUCTURAL_DRIFT"]))
        event = engine.emit_response_event(response, drift_report_id="drift-report::001")

        self.assertEqual("DRIFT_RESPONSE_GENERATED", event["event_type"])
        self.assertEqual("drift-report::001", event["payload"]["drift_report_id"])
        self.assertEqual("STAGE_FIX", event["payload"]["response_type"])
        self.assertFalse(event["payload"]["staged_proposal"]["auto_apply"])

    def test_drift_response_event_schema_is_valid_json(self):
        schema = json.loads(
            (ROOT / "contracts" / "drift_response_event.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual("object", schema["type"])
        self.assertIn("event_type", schema["required"])
        self.assertIn("payload", schema["required"])


if __name__ == "__main__":
    unittest.main()
