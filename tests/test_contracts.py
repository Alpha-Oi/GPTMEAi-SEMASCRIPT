import json
import unittest
from pathlib import Path

from bridge.semascript_validator import validate_action_document


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_contract_schemas_are_valid_json_and_define_required_fields(self):
        expected_required = {
            "semascript_action_document.schema.json": {
                "version",
                "source",
                "intent",
                "actions",
                "constraints",
                "safety",
                "metadata",
            },
            "gptmeai_planner_preview.schema.json": {
                "version",
                "preview_id",
                "status",
                "mapped_actions",
                "required_approvals",
                "risks",
                "dry_run",
                "metadata",
            },
            "execution_approval.schema.json": {
                "approval_id",
                "preview_id",
                "approved",
                "approved_by",
                "scope",
                "expires_at",
                "metadata",
            },
            "adapter_error_model.schema.json": {
                "error_code",
                "message",
                "severity",
                "source",
                "retryable",
                "details",
            },
        }

        for filename, required_fields in expected_required.items():
            with self.subTest(filename=filename):
                schema = json.loads((ROOT / "contracts" / filename).read_text(encoding="utf-8"))
                self.assertEqual(schema["type"], "object")
                self.assertTrue(required_fields.issubset(set(schema["required"])))

    def test_valid_action_document_passes_manual_validation(self):
        document = json.loads(
            (ROOT / "tests" / "fixtures" / "semascript_action_document.valid.json").read_text(
                encoding="utf-8"
            )
        )

        result = validate_action_document(document)

        self.assertTrue(result["valid"], result)
        self.assertEqual([], result["errors"])

    def test_invalid_action_document_fails_manual_validation(self):
        document = json.loads(
            (ROOT / "tests" / "fixtures" / "semascript_action_document.invalid.json").read_text(
                encoding="utf-8"
            )
        )

        result = validate_action_document(document)

        self.assertFalse(result["valid"])
        self.assertGreaterEqual(len(result["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
