import unittest

from core.risk_engine import RiskEngine


class RiskEngineTests(unittest.TestCase):
    def test_blocked_risk_overrides_execution(self):
        engine = RiskEngine()
        proposal = {
            "proposal_id": "proposal::blocked",
            "actions": [{"operation": "direct_runtime_mutation", "target": "runtime"}],
        }

        first = engine.classify(proposal)
        second = engine.classify(proposal)

        self.assertEqual(first, second)
        self.assertEqual("BLOCKED", first["risk_level"])
        self.assertTrue(engine.block_if_needed(first)["blocked"])

    def test_readonly_documentation_action_is_low_risk(self):
        engine = RiskEngine()
        result = engine.classify(
            {
                "proposal_id": "proposal::safe",
                "actions": [{"operation": "document", "target": "artifacts"}],
            }
        )

        self.assertEqual("LOW", result["risk_level"])
        self.assertFalse(engine.block_if_needed(result)["blocked"])


if __name__ == "__main__":
    unittest.main()
