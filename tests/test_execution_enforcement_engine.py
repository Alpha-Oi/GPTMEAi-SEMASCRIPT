import json
import unittest
from pathlib import Path

from execution_enforcement import ExecutionEnforcementEngine


ROOT = Path(__file__).resolve().parents[1]


class ExecutionEnforcementEngineTests(unittest.TestCase):
    def drift_response_event(self, response_type, action):
        return {
            "event_id": f"event::drift-response::001::{response_type.lower()}",
            "event_type": "DRIFT_RESPONSE_GENERATED",
            "artifact_id": "drift-response-layer::1.0",
            "payload": {
                "drift_report_id": "drift-report::001",
                "response_type": response_type,
                "reasoning": "test response",
                "staged_proposal": {
                    "proposal_id": f"drift-correction::{response_type.lower()}",
                    "action": action,
                    "auto_apply": False,
                    "runtime_mutation": False,
                    "requires_governance_approval": response_type
                    in {"BLOCK_EXECUTION", "STAGE_FIX", "ROLLBACK"},
                },
            },
        }

    def approval(self, approved=True):
        return {
            "approved": approved,
            "decision": "APPROVED" if approved else "REJECTED",
            "approved_by": "governance-board" if approved else "",
        }

    def risk(self, level="LOW"):
        return {"risk_level": level, "score": 10 if level == "LOW" else 100}

    def test_blocked_action_enforcement_has_highest_priority(self):
        engine = ExecutionEnforcementEngine()
        result = engine.evaluate_response(
            self.drift_response_event("BLOCK_EXECUTION", "block_execution"),
            governance_approval=self.approval(True),
            risk_result=self.risk("LOW"),
        )

        self.assertEqual("BLOCK_EXECUTION", result["action_type"])
        self.assertEqual("BLOCKED", result["execution_status"])
        self.assertEqual([], result["applied_changes"])
        self.assertTrue(result["event_emitted"])
        self.assertEqual("EXECUTION_ENFORCED", result["event"]["event_type"])

    def test_rollback_requires_governance_approval(self):
        engine = ExecutionEnforcementEngine()
        result = engine.evaluate_response(
            self.drift_response_event("ROLLBACK", "stage_rollback"),
            governance_approval=self.approval(False),
            risk_result=self.risk("LOW"),
        )

        self.assertEqual("ROLLBACK_STATE", result["action_type"])
        self.assertEqual("REJECTED", result["execution_status"])
        self.assertEqual([], result["applied_changes"])

    def test_approved_rollback_is_audited_without_runtime_mutation(self):
        result = ExecutionEnforcementEngine().evaluate_response(
            self.drift_response_event("ROLLBACK", "stage_rollback"),
            governance_approval=self.approval(True),
            risk_result=self.risk("LOW"),
        )

        self.assertEqual("ROLLBACK_STATE", result["action_type"])
        self.assertEqual("APPROVED", result["execution_status"])
        self.assertIn("AUDIT_ONLY: ROLLBACK_STATE", result["applied_changes"])
        self.assertFalse(result["runtime_mutation"])

    def test_governance_override_cannot_approve_blocked_risk(self):
        result = ExecutionEnforcementEngine().evaluate_response(
            self.drift_response_event("STAGE_FIX", "stage_fix"),
            governance_approval=self.approval(True),
            risk_result=self.risk("BLOCKED"),
        )

        self.assertEqual("APPLY_FIX", result["action_type"])
        self.assertEqual("BLOCKED", result["execution_status"])
        self.assertEqual([], result["applied_changes"])

    def test_no_action_logging_correctness(self):
        result = ExecutionEnforcementEngine().evaluate_response(
            self.drift_response_event("NO_ACTION", ""),
            governance_approval=self.approval(False),
            risk_result=self.risk("LOW"),
        )

        self.assertEqual("NO_ACTION", result["action_type"])
        self.assertEqual("APPROVED", result["execution_status"])
        self.assertEqual(["AUDIT_ONLY: NO_ACTION"], result["applied_changes"])

    def test_deterministic_execution_replay(self):
        event = self.drift_response_event("STAGE_FIX", "stage_fix")
        approval = self.approval(True)
        risk = self.risk("LOW")
        engine = ExecutionEnforcementEngine()

        self.assertEqual(
            engine.evaluate_response(event, approval, risk),
            engine.evaluate_response(event, approval, risk),
        )

    def test_execution_enforced_event_schema_is_valid_json(self):
        schema = json.loads(
            (ROOT / "contracts" / "execution_enforced_event.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("object", schema["type"])
        self.assertIn("event_type", schema["required"])
        self.assertIn("payload", schema["required"])


if __name__ == "__main__":
    unittest.main()
