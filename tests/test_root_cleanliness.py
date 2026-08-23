import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tools.check_root_cleanliness import check_root_cleanliness, main


ROOT = Path(__file__).resolve().parents[1]


class RootCleanlinessTests(unittest.TestCase):
    def test_current_project_root_passes(self):
        result = check_root_cleanliness(ROOT)

        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["violations"])

    def test_root_report_file_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "SOME_REPORT.md").write_text("# report\n", encoding="utf-8")

            result = check_root_cleanliness(root)

        self.assertFalse(result["ok"])
        self.assertIn("root report file: SOME_REPORT.md", result["violations"])

    def test_report_under_reports_codex_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "reports" / "codex"
            report_dir.mkdir(parents=True)
            (report_dir / "SOME_REPORT.md").write_text("# report\n", encoding="utf-8")

            result = check_root_cleanliness(root)

        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["violations"])

    def test_forbidden_root_folder_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "node_modules").mkdir()

            result = check_root_cleanliness(root)

        self.assertFalse(result["ok"])
        self.assertIn("forbidden root entry: node_modules", result["violations"])

    def test_exact_git_root_entry_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()

            result = check_root_cleanliness(root)

        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["violations"])

    def test_git_like_root_entries_fail(self):
        for entry_name in (".git_backup", ".git-old", ".git.tmp"):
            with self.subTest(entry_name=entry_name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    (root / entry_name).mkdir()

                    result = check_root_cleanliness(root)

                self.assertFalse(result["ok"])
                self.assertIn(
                    f"forbidden root entry: {entry_name}", result["violations"]
                )

    def test_main_preserves_success_and_failure_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()
            output = StringIO()

            with redirect_stdout(output):
                success_exit_code = main([str(root)])

            self.assertEqual(0, success_exit_code)
            self.assertIn("ROOT_CLEANLINESS=OK", output.getvalue())

            (root / "node_modules").mkdir()
            output = StringIO()

            with redirect_stdout(output):
                failure_exit_code = main([str(root)])

            self.assertEqual(1, failure_exit_code)
            self.assertIn("ROOT_CLEANLINESS=FAIL", output.getvalue())
            self.assertIn("forbidden root entry: node_modules", output.getvalue())


if __name__ == "__main__":
    unittest.main()
