import unittest

from core.event_store import EventStore
from core.governance import GovernanceEngine
from core.risk_engine import RiskEngine
from core.state_engine import StateEngine
from core.validation_engine import ValidationEngine


class ValidationTests(unittest.TestCase):
    def test_validation_detects_drift(self):
        store = EventStore()
        store.append(
            {
                "event_id": "event::drift",
                "event_type": "ARTIFACT_REGISTERED",
                "artifact_id": "artifact::drift",
                "payload": {"state": "ACTIVE", "type": "demo"},
            }
        )
        engine = StateEngine()
        state = engine.rebuild(store.get_all())
        drifted = dict(state)
        drifted["events_applied"] = 99

        result = ValidationEngine().check_drift(store.get_all(), drifted)

        self.assertTrue(result["drift_detected"])

    def test_governance_is_deterministic_and_uses_risk(self):
        risk = RiskEngine().classify(
            {
                "proposal_id": "proposal::governance",
                "artifact_type": "implementation_root_skeleton",
                "actions": [{"operation": "document", "target": "artifacts"}],
            }
        )
        state = {
            "artifacts": {
                "artifact::candidate": {
                    "artifact_id": "artifact::candidate",
                    "type": "implementation_root_skeleton",
                    "state": "ACTIVE",
                    "trust": "high",
                }
            }
        }
        proposal = {"proposal_id": "proposal::governance", "artifact_type": "implementation_root_skeleton"}
        governance = GovernanceEngine()

        first = governance.evaluate(proposal, state, risk)
        second = governance.evaluate(proposal, state, risk)

        self.assertEqual(first, second)
        self.assertEqual("artifact::candidate", first["canonical_artifact_id"])


if __name__ == "__main__":
    unittest.main()
