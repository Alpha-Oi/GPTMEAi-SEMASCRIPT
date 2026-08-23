import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "stage4_preview_handoff_contract.v0.1.json"

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


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class Stage4PreviewHandoffContractTests(unittest.TestCase):
    def test_contract_file_exists(self):
        self.assertTrue(CONTRACT.is_file(), f"missing contract: {CONTRACT}")

    def test_contract_is_valid_json_and_identifies_stage4_preview_handoff(self):
        contract = load_contract()

        self.assertEqual("STAGE4_PREVIEW_HANDOFF", contract["contract_id"])
        self.assertEqual("Stage 4 Preview Handoff Contract", contract["name"])
        self.assertEqual("0.1", contract["version"])
        self.assertIn("draft", contract["status"])

    def test_safety_flags_are_present_and_non_mutating(self):
        flags = load_contract()["mode_flags"]

        self.assertIs(flags["dry_run"], True)
        self.assertIs(flags["preview_only"], True)
        self.assertIs(flags["execution_allowed"], False)
        self.assertIs(flags["mutation_allowed"], False)
        self.assertIs(flags["requires_human_approval"], True)

    def test_required_boundary_sections_are_present(self):
        contract = load_contract()
        missing = [section for section in REQUIRED_SECTIONS if section not in contract]

        self.assertEqual([], missing)

    def test_mutation_boundaries_cover_required_prohibitions(self):
        boundaries = set(load_contract()["mutation_boundaries"])

        self.assertTrue(REQUIRED_MUTATION_BOUNDARIES.issubset(boundaries))

    def test_explicit_non_goals_do_not_authorize_execution(self):
        non_goals = set(load_contract()["explicit_non_goals"])

        self.assertTrue(REQUIRED_NON_GOALS.issubset(non_goals))

    def test_contract_does_not_authorize_runtime_execution(self):
        contract = load_contract()
        serialized = json.dumps(contract, sort_keys=True)

        self.assertFalse(contract["mode_flags"]["execution_allowed"])
        self.assertFalse(contract["mode_flags"]["mutation_allowed"])
        self.assertNotIn('"execute": true', serialized)
        self.assertNotIn('"planner_execution": true', serialized)
        self.assertNotIn('"runtime_mutation": true', serialized)

    def test_handoff_stops_at_approval_gate(self):
        stages = load_contract()["validation_stages"]
        stage_ids = [stage["id"] for stage in stages]

        self.assertEqual(
            [
                "validate_semascript_action_document",
                "normalize_action_document",
                "build_planner_preview_handoff",
                "stop_at_approval_gate",
            ],
            stage_ids,
        )


if __name__ == "__main__":
    unittest.main()
