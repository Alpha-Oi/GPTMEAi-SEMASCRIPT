import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "local_workspace.py"


class LocalWorkspaceCliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_root = Path(self.temp_dir.name)
        self.workspace = self.temp_root / "workspace.json"

    def run_cli(self, *arguments):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONUTF8"] = "1"
        return subprocess.run(
            [sys.executable, "-B", str(CLI), *map(str, arguments)],
            cwd=str(ROOT),
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def assert_success_json(self, completed, command):
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual(command, payload["command"])
        return payload

    def assert_error_json(self, completed, error_code):
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        payload = json.loads(completed.stderr)
        self.assertEqual("error", payload["status"])
        self.assertEqual(error_code, payload["error_code"])
        self.assertIsInstance(payload["message"], str)
        self.assertTrue(payload["message"])
        return payload

    def test_separate_process_restart_round_trip_and_readonly_bytes(self):
        initialized = self.assert_success_json(
            self.run_cli("init", self.workspace),
            "init",
        )
        self.assertEqual(0, initialized["artifact_count"])

        first_add = self.assert_success_json(
            self.run_cli(
                "add",
                self.workspace,
                "--id",
                "zeta",
                "--title",
                "Последняя заметка",
                "--content",
                "Привет, мир 🌍",
            ),
            "add",
        )
        self.assertEqual(1, first_add["artifact_count"])
        second_add = self.assert_success_json(
            self.run_cli(
                "add",
                self.workspace,
                "--id",
                "alpha",
                "--title",
                "First note",
                "--content",
                "Offline knowledge",
            ),
            "add",
        )
        self.assertEqual(2, second_add["artifact_count"])

        before_readonly = self.workspace.read_bytes()
        listed = self.assert_success_json(self.run_cli("list", self.workspace), "list")
        searched = self.assert_success_json(
            self.run_cli("search", self.workspace, "ПРИВЕТ"),
            "search",
        )
        validated = self.assert_success_json(
            self.run_cli("validate", self.workspace),
            "validate",
        )

        self.assertEqual(["alpha", "zeta"], [item["artifact_id"] for item in listed["artifacts"]])
        self.assertEqual(2, listed["artifact_count"])
        self.assertEqual(1, searched["match_count"])
        self.assertEqual("Привет, мир 🌍", searched["artifacts"][0]["content"])
        self.assertEqual(2, validated["artifact_count"])
        self.assertEqual(before_readonly, self.workspace.read_bytes())
        self.assertIn("Привет, мир 🌍", self.workspace.read_text(encoding="utf-8"))
        self.assertFalse(self.workspace.resolve().is_relative_to(ROOT.resolve()))

    def test_duplicate_add_and_second_init_preserve_bytes(self):
        self.assert_success_json(self.run_cli("init", self.workspace), "init")
        self.assert_success_json(
            self.run_cli(
                "add",
                self.workspace,
                "--id",
                "same",
                "--title",
                "Title",
                "--content",
                "Content",
            ),
            "add",
        )
        before = self.workspace.read_bytes()

        duplicate = self.run_cli(
            "add",
            self.workspace,
            "--id",
            "same",
            "--title",
            "Other",
            "--content",
            "Other",
        )
        self.assert_error_json(duplicate, "DUPLICATE_ARTIFACT_ID")
        self.assertEqual(before, self.workspace.read_bytes())

        second_init = self.run_cli("init", self.workspace)
        self.assert_error_json(second_init, "WORKSPACE_ALREADY_EXISTS")
        self.assertEqual(before, self.workspace.read_bytes())

    def test_corrupt_workspace_and_missing_workspace_are_json_errors_without_rewrite(self):
        corrupt = self.temp_root / "corrupt.json"
        corrupt.write_bytes(b'{"format": invalid')
        before = corrupt.read_bytes()

        invalid = self.run_cli("validate", corrupt)
        self.assert_error_json(invalid, "INVALID_JSON")
        self.assertEqual(before, corrupt.read_bytes())

        missing = self.run_cli("list", self.temp_root / "missing.json")
        self.assert_error_json(missing, "WORKSPACE_NOT_FOUND")

    def test_help_succeeds_and_argument_errors_are_json(self):
        help_result = self.run_cli("--help")
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        self.assertIn("init", help_result.stdout)
        self.assertIn("add", help_result.stdout)
        self.assertIn("list", help_result.stdout)
        self.assertIn("search", help_result.stdout)
        self.assertIn("validate", help_result.stdout)

        invalid = self.run_cli("add", self.workspace)
        self.assert_error_json(invalid, "INVALID_ARGUMENT")

    def test_empty_search_query_is_json_error_and_does_not_mutate(self):
        self.assert_success_json(self.run_cli("init", self.workspace), "init")
        before = self.workspace.read_bytes()

        invalid = self.run_cli("search", self.workspace, "   ")

        self.assert_error_json(invalid, "INVALID_ARGUMENT")
        self.assertEqual(before, self.workspace.read_bytes())

    def test_cli_leaves_no_runtime_workspace_or_temp_sibling_in_repository(self):
        self.assert_success_json(self.run_cli("init", self.workspace), "init")
        self.assert_success_json(
            self.run_cli(
                "add",
                self.workspace,
                "--id",
                "outside-repo",
                "--title",
                "Outside",
                "--content",
                "Temporary-directory workspace",
            ),
            "add",
        )

        self.assertFalse((ROOT / "workspace.json").exists())
        self.assertEqual([], list(ROOT.glob(".workspace.json.*.tmp")))
        self.assertFalse(self.workspace.resolve().is_relative_to(ROOT.resolve()))


if __name__ == "__main__":
    unittest.main()
