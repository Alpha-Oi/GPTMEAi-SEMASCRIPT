import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools" / "run_local_verification.py"


class LocalVerificationWrapperTests(unittest.TestCase):
    def load_wrapper_module(self):
        self.assertTrue(WRAPPER.is_file(), "run_local_verification.py is missing")
        spec = importlib.util.spec_from_file_location("run_local_verification", WRAPPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_wrapper_script_exists(self):
        self.assertTrue(WRAPPER.is_file())

    def test_expected_commands_are_defined_in_order(self):
        module = self.load_wrapper_module()
        commands = [" ".join(command) for command in module.CHECK_COMMANDS]

        self.assertEqual(
            [
                "python -B tools\\check_root_cleanliness.py",
                "python -B tools\\check_schema_consistency.py",
                "python -B -m unittest discover -s tests",
                "python -B tools\\verify_bridge.py",
                "python -B tools\\collect_source_references.py",
            ],
            commands,
        )

    def test_report_path_is_under_reports_codex(self):
        module = self.load_wrapper_module()
        report_path = module.report_path(ROOT)

        self.assertEqual(ROOT / "reports" / "codex" / "LOCAL_SMOKE_WRAPPER_REPORT.md", report_path)

    def test_report_path_is_not_project_root(self):
        module = self.load_wrapper_module()
        report_path = module.report_path(ROOT)

        self.assertNotEqual(ROOT / "LOCAL_SMOKE_WRAPPER_REPORT.md", report_path)
        self.assertEqual(ROOT / "reports" / "codex", report_path.parent)

    def test_wrapper_does_not_include_dependency_install_commands(self):
        module = self.load_wrapper_module()
        command_text = "\n".join(" ".join(command).lower() for command in module.CHECK_COMMANDS)

        for forbidden in ("pip install", "python -m pip", "poetry install", "npm install"):
            self.assertNotIn(forbidden, command_text)

    def test_wrapper_does_not_include_execution_or_mutation_commands(self):
        module = self.load_wrapper_module()
        command_text = "\n".join(" ".join(command).lower() for command in module.CHECK_COMMANDS)
        source_text = WRAPPER.read_text(encoding="utf-8").lower()

        for forbidden in ("execute", "mutation", "runtime start", "run_ai_os.py"):
            self.assertNotIn(forbidden, command_text)
        self.assertNotIn(".execute(", source_text)


if __name__ == "__main__":
    unittest.main()
