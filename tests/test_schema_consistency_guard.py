import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "check_schema_consistency.py"
TEMP_ROOT = ROOT / "tests"
SCHEMA_FILES = (
    "semascript_action_document.schema.json",
    "gptmeai_planner_preview.schema.json",
    "execution_approval.schema.json",
    "adapter_error_model.schema.json",
    "gptmeai_readonly_status_snapshot.schema.json",
)


def load_checker():
    if not TOOL.is_file():
        raise AssertionError("check_schema_consistency.py is missing")
    spec = importlib.util.spec_from_file_location("check_schema_consistency", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_current_matrix():
    return json.loads(
        (ROOT / "contracts" / "compatibility_matrix.v0.1.json").read_text(
            encoding="utf-8"
        )
    )


def make_fake_project_root(matrix):
    temp_dir = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
    root = Path(temp_dir.name)
    contracts = root / "contracts"
    docs = root / "docs"
    contracts.mkdir()
    docs.mkdir()
    for filename in SCHEMA_FILES:
        source = ROOT / "contracts" / filename
        (contracts / filename).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (contracts / "compatibility_matrix.v0.1.json").write_text(
        json.dumps(matrix, indent=2),
        encoding="utf-8",
    )
    (docs / "05_CONTRACT_COMPATIBILITY_MATRIX.md").write_text(
        (ROOT / "docs" / "05_CONTRACT_COMPATIBILITY_MATRIX.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return temp_dir, root


class SchemaConsistencyGuardTests(unittest.TestCase):
    def test_checker_script_exists(self):
        self.assertTrue(TOOL.is_file())

    def test_current_project_schema_consistency_check_passes(self):
        checker = load_checker()

        result = checker.check_consistency(ROOT)

        self.assertTrue(result["ok"], result)

    def test_action_document_required_fields_are_present_in_matrix(self):
        checker = load_checker()
        schema = checker.load_json(ROOT / "contracts" / "semascript_action_document.schema.json")
        matrix = load_current_matrix()

        required = set(checker.schema_required_fields(schema))
        matrix_fields = checker.matrix_field_names(matrix, "semascript_action_document")

        self.assertTrue(required.issubset(matrix_fields))

    def test_planner_preview_required_fields_are_present_in_matrix(self):
        checker = load_checker()
        schema = checker.load_json(ROOT / "contracts" / "gptmeai_planner_preview.schema.json")
        matrix = load_current_matrix()

        required = set(checker.schema_required_fields(schema))
        matrix_fields = checker.matrix_field_names(matrix, "planner_preview")

        self.assertTrue(required.issubset(matrix_fields))

    def test_readonly_status_snapshot_required_fields_are_present_in_matrix(self):
        checker = load_checker()
        schema = checker.load_json(
            ROOT / "contracts" / "gptmeai_readonly_status_snapshot.schema.json"
        )
        matrix = load_current_matrix()

        required = set(checker.schema_required_fields(schema))
        matrix_fields = checker.matrix_field_names(matrix, "gptmeai_readonly_status_snapshot")

        self.assertTrue(required.issubset(matrix_fields))

    def test_matrix_scope_is_dry_run(self):
        matrix = load_current_matrix()

        self.assertEqual("dry-run", matrix["scope"])

    def test_unsupported_v01_contains_core_boundaries(self):
        checker = load_checker()
        unsupported = checker.unsupported_items(load_current_matrix())

        self.assertTrue(
            {
                "real execution",
                "memory mutation",
                "storage mutation",
                "ledger mutation",
            }.issubset(unsupported)
        )

    def test_fake_matrix_missing_required_action_field_fails(self):
        checker = load_checker()
        matrix = load_current_matrix()
        matrix["semascript_action_document"]["fields"] = [
            field
            for field in matrix["semascript_action_document"]["fields"]
            if field["name"] != "intent"
        ]
        temp_dir, fake_root = make_fake_project_root(matrix)
        self.addCleanup(temp_dir.cleanup)

        result = checker.check_consistency(fake_root)

        self.assertFalse(result["ok"])
        self.assertTrue(
            any("semascript_action_document missing required fields" in error for error in result["errors"]),
            result,
        )

    def test_fake_matrix_marking_execution_supported_fails(self):
        checker = load_checker()
        matrix = load_current_matrix()
        matrix["unsupported_v0_1"][0]["status"] = "supported"
        temp_dir, fake_root = make_fake_project_root(matrix)
        self.addCleanup(temp_dir.cleanup)

        result = checker.check_consistency(fake_root)

        self.assertFalse(result["ok"])
        self.assertTrue(
            any("unsupported item is marked supported" in error for error in result["errors"]),
            result,
        )


if __name__ == "__main__":
    unittest.main()
