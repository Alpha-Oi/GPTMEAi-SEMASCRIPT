import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "05_CONTRACT_COMPATIBILITY_MATRIX.md"
MATRIX_PATH = ROOT / "contracts" / "compatibility_matrix.v0.1.json"


def load_matrix_file():
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


class ContractCompatibilityMatrixTests(unittest.TestCase):
    def test_documentation_matrix_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_machine_readable_matrix_exists_and_is_valid_json(self):
        self.assertTrue(MATRIX_PATH.is_file())
        matrix = load_matrix_file()

        self.assertEqual("0.1", matrix["version"])

    def test_matrix_scope_is_dry_run(self):
        matrix = load_matrix_file()

        self.assertEqual("dry-run", matrix["scope"])

    def test_required_action_document_fields_are_listed(self):
        matrix = load_matrix_file()
        fields = {
            field["name"]
            for field in matrix["semascript_action_document"]["fields"]
        }

        self.assertTrue(
            {
                "version",
                "source",
                "intent",
                "actions[]",
                "constraints",
                "safety",
                "metadata",
            }.issubset(fields)
        )

    def test_planner_preview_fields_are_listed(self):
        matrix = load_matrix_file()
        fields = {field["name"] for field in matrix["planner_preview"]["fields"]}

        self.assertTrue(
            {
                "preview_id",
                "status",
                "mapped_actions[]",
                "required_approvals[]",
                "risks[]",
                "dry_run",
                "metadata",
            }.issubset(fields)
        )

    def test_unsupported_v01_includes_mutation_boundaries(self):
        matrix = load_matrix_file()
        unsupported = {item["name"] for item in matrix["unsupported_v0_1"]}

        self.assertTrue(
            {
                "real execution",
                "memory mutation",
                "storage mutation",
                "ledger mutation",
            }.issubset(unsupported)
        )

    def test_loader_loads_default_matrix(self):
        from bridge.compatibility_matrix import load_compatibility_matrix

        matrix = load_compatibility_matrix()

        self.assertEqual("0.1", matrix["version"])
        self.assertEqual("dry-run", matrix["scope"])

    def test_get_field_status_returns_intent_data(self):
        from bridge.compatibility_matrix import get_field_status, load_compatibility_matrix

        matrix = load_compatibility_matrix()
        intent = get_field_status(matrix, "semascript_action_document", "intent")

        self.assertIsNotNone(intent)
        self.assertEqual("intent", intent["name"])
        self.assertIn(intent["status"], {"required", "supported"})

    def test_list_unsupported_v01_returns_non_empty_list(self):
        from bridge.compatibility_matrix import (
            list_unsupported_v0_1,
            load_compatibility_matrix,
        )

        unsupported = list_unsupported_v0_1(load_compatibility_matrix())

        self.assertGreater(len(unsupported), 0)

    def test_no_entry_claims_real_execution_is_supported(self):
        matrix = load_matrix_file()
        unsupported = {item["name"] for item in matrix["unsupported_v0_1"]}

        self.assertIn("real execution", unsupported)
        for item in matrix["unsupported_v0_1"]:
            if item["name"] == "real execution":
                self.assertNotEqual("supported", item.get("status"))
                self.assertEqual("unsupported-v0.1", item["status"])


if __name__ == "__main__":
    unittest.main()
