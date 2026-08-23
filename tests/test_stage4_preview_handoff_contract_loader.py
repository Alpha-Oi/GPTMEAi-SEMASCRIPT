import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "stage4_preview_handoff_contract.py"
CONTRACT = ROOT / "contracts" / "stage4_preview_handoff_contract.v0.1.json"
TEMP_ROOT = ROOT / "tests"


def load_tool_module():
    if not TOOL.is_file():
        raise AssertionError(f"missing helper: {TOOL}")
    spec = importlib.util.spec_from_file_location("stage4_preview_handoff_contract", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage4PreviewHandoffContractLoaderTests(unittest.TestCase):
    def setUp(self):
        self.module = load_tool_module()
        self.contract = self.module.load_stage4_preview_handoff_contract()

    def test_loader_can_load_default_contract(self):
        self.assertEqual("STAGE4_PREVIEW_HANDOFF", self.contract["contract_id"])

    def test_loaded_contract_validates_with_no_errors(self):
        errors = self.module.validate_stage4_preview_handoff_contract(self.contract)

        self.assertEqual([], errors)

    def test_assert_accepts_current_valid_contract(self):
        self.module.assert_stage4_preview_handoff_contract_valid(self.contract)

    def test_missing_or_changed_contract_id_fails_validation(self):
        for value in (None, "WRONG_CONTRACT"):
            with self.subTest(contract_id=value):
                contract = copy.deepcopy(self.contract)
                if value is None:
                    contract.pop("contract_id")
                else:
                    contract["contract_id"] = value

                errors = self.module.validate_stage4_preview_handoff_contract(contract)

                self.assertTrue(any("contract_id" in error for error in errors), errors)

    def test_unsafe_mode_flags_fail_validation(self):
        unsafe_cases = (
            ("dry_run", False),
            ("preview_only", False),
            ("execution_allowed", True),
            ("mutation_allowed", True),
            ("requires_human_approval", False),
        )
        for flag, value in unsafe_cases:
            with self.subTest(flag=flag):
                contract = copy.deepcopy(self.contract)
                contract["mode_flags"][flag] = value

                errors = self.module.validate_stage4_preview_handoff_contract(contract)

                self.assertTrue(any(f"mode_flags.{flag}" in error for error in errors), errors)

    def test_missing_required_sections_fail_validation(self):
        for section in self.module.REQUIRED_SECTIONS:
            with self.subTest(section=section):
                contract = copy.deepcopy(self.contract)
                contract.pop(section)

                errors = self.module.validate_stage4_preview_handoff_contract(contract)

                self.assertTrue(any(section in error for error in errors), errors)

    def test_missing_required_non_goals_or_mutation_boundaries_fail_validation(self):
        contract = copy.deepcopy(self.contract)
        contract["explicit_non_goals"].remove("no planner execution")

        errors = self.module.validate_stage4_preview_handoff_contract(contract)

        self.assertTrue(any("explicit_non_goals" in error for error in errors), errors)

        contract = copy.deepcopy(self.contract)
        contract["mutation_boundaries"].remove("no ledger mutation")

        errors = self.module.validate_stage4_preview_handoff_contract(contract)

        self.assertTrue(any("mutation_boundaries" in error for error in errors), errors)

    def test_assert_raises_value_error_with_clear_message(self):
        contract = copy.deepcopy(self.contract)
        contract["mode_flags"]["execution_allowed"] = True

        with self.assertRaises(ValueError) as context:
            self.module.assert_stage4_preview_handoff_contract_valid(contract)

        self.assertIn("mode_flags.execution_allowed", str(context.exception))

    def test_explicit_path_loads_temp_contract_without_writing(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
            temp_contract = Path(temp_dir) / "contract.json"
            original = json.dumps(self.contract, indent=2)
            temp_contract.write_text(original, encoding="utf-8")

            loaded = self.module.load_stage4_preview_handoff_contract(temp_contract)
            self.module.assert_stage4_preview_handoff_contract_valid(loaded)

            self.assertEqual(original, temp_contract.read_text(encoding="utf-8"))

    def test_helper_has_no_runtime_network_or_write_primitives(self):
        source = TOOL.read_text(encoding="utf-8").lower()

        for forbidden in (
            "urllib",
            "requests",
            "socket",
            "subprocess",
            "http.client",
            "write_text",
            "open(",
            ".execute(",
            "run_ai_os.py",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
