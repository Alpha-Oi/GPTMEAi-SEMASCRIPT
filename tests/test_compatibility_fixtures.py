import json
import unittest
from pathlib import Path

from adapters.semascript.ast_adapter import normalize_semascript_ast
from bridge.approval_gate import require_approval
from bridge.gptmeai_client import GPTMEAiReadOnlyClient
from bridge.planner_preview_adapter import map_semascript_to_planner_preview
from bridge.semascript_validator import validate_action_document


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "compatibility"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class CompatibilityFixtureTests(unittest.TestCase):
    def test_semascript_ast_fixture_normalizes_to_expected_action_document(self):
        ast_document = load_fixture("semascript_ast.sample.json")
        expected = load_fixture("semascript_action_document.from_ast.sample.json")

        normalized = normalize_semascript_ast(ast_document)

        self.assertEqual(expected, normalized)

    def test_normalized_ast_document_passes_bridge_validation(self):
        ast_document = load_fixture("semascript_ast.sample.json")
        normalized = normalize_semascript_ast(ast_document)

        validation = validate_action_document(normalized)

        self.assertTrue(validation["valid"], validation)
        self.assertEqual([], validation["errors"])

    def test_planner_preview_from_ast_fixture_is_dry_run_and_requires_approval(self):
        ast_document = load_fixture("semascript_ast.sample.json")
        normalized = normalize_semascript_ast(ast_document)

        preview = map_semascript_to_planner_preview(normalized)

        self.assertTrue(preview["dry_run"])
        self.assertTrue(require_approval(preview))
        self.assertGreaterEqual(len(preview["required_approvals"]), 1)

    def test_planner_preview_matches_expected_essentials(self):
        ast_document = load_fixture("semascript_ast.sample.json")
        expected = load_fixture("adapter_preview.expected.json")
        normalized = normalize_semascript_ast(ast_document)

        preview = map_semascript_to_planner_preview(normalized)

        self.assertEqual(expected["version"], preview["version"])
        self.assertEqual(expected["status"], preview["status"])
        self.assertEqual(expected["dry_run"], preview["dry_run"])
        self.assertGreaterEqual(
            len(preview["required_approvals"]),
            expected["required_approvals_min"],
        )
        self.assertEqual(len(expected["mapped_actions"]), len(preview["mapped_actions"]))
        for expected_action, preview_action in zip(expected["mapped_actions"], preview["mapped_actions"]):
            self.assertEqual(expected_action["source_action_id"], preview_action["source_action_id"])
            self.assertEqual(expected_action["operation"], preview_action["operation"])
            self.assertEqual(expected_action["execution_mode"], preview_action["execution_mode"])
            self.assertIn(expected_action["planner_step_contains"], preview_action["planner_step"])
        for key, value in expected["metadata"].items():
            self.assertEqual(value, preview["metadata"][key])

    def test_gptmeai_status_payload_fixtures_are_safe_read_only_shapes(self):
        health = load_fixture("gptmeai_health.sample.json")
        planner = load_fixture("gptmeai_planner_status.sample.json")
        execution = load_fixture("gptmeai_execution_status.sample.json")

        self.assertEqual("ok", health["status"])
        self.assertEqual("AI OS API", health["service"])
        self.assertIn("planner_active", health)
        self.assertIn("execution_failed", health)

        self.assertEqual("ok", planner["status"])
        self.assertIn("plan_counts", planner)
        self.assertIn("step_counts", planner)
        self.assertIn("plans", planner)

        self.assertEqual("ok", execution["status"])
        self.assertIn("operation_counts", execution)
        self.assertIn("compensation_counts", execution)
        self.assertIn("operations", execution)

    def test_gptmeai_client_remains_read_only_without_execute_or_mutation_methods(self):
        client = GPTMEAiReadOnlyClient("http://127.0.0.1:8010", timeout=0.1)

        for forbidden_method in (
            "execute",
            "mutate",
            "add_memory",
            "delete_memory",
            "queue_task",
            "dispatch",
        ):
            with self.subTest(forbidden_method=forbidden_method):
                self.assertFalse(hasattr(client, forbidden_method))

        for allowed_method in ("health", "planner_status", "execution_status"):
            with self.subTest(allowed_method=allowed_method):
                self.assertTrue(callable(getattr(client, allowed_method)))


if __name__ == "__main__":
    unittest.main()
