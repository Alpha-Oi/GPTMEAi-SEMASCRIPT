import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "compatibility"
TOOL = ROOT / "tools" / "write_gptmeai_readonly_snapshot_from_report.py"
LOCAL_VERIFICATION = ROOT / "tools" / "run_local_verification.py"
REPORT_FIXTURE = FIXTURES / "gptmeai_live_readonly_report.unavailable.md"
EXPECTED_FIXTURE = (
    FIXTURES / "gptmeai_live_readonly_snapshot_from_report.expected.json"
)
FORBIDDEN_TOOL_TEXT = (
    "GPTMEAiReadOnlyClient",
    "check_gptmeai_live_readonly",
    "/execute",
    "/execution/run",
    "/memory/add",
    "/memory/delete",
    "/ledger/write",
    ".execute(",
)


class WriteGPTMEAiReadonlySnapshotFromReportTests(unittest.TestCase):
    def test_cli_tool_exists(self):
        self.assertTrue(TOOL.is_file())

    def test_default_output_path_is_under_reports_codex(self):
        from tools.write_gptmeai_readonly_snapshot_from_report import (
            default_output_path,
        )

        output = default_output_path(ROOT)

        self.assertEqual(ROOT / "reports" / "codex", output.parent)
        self.assertEqual("GPTMEAI_READONLY_STATUS_SNAPSHOT_FROM_LIVE_REPORT.json", output.name)

    def test_write_snapshot_from_report_creates_expected_json(self):
        from tools.write_gptmeai_readonly_snapshot_from_report import (
            write_snapshot_from_report,
        )

        expected = json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "snapshot.json"

            written_path = write_snapshot_from_report(
                report_path=REPORT_FIXTURE,
                output_path=output_path,
                captured_at="2026-05-03T00:00:00Z",
            )

            self.assertEqual(output_path, written_path)
            self.assertTrue(output_path.is_file())
            self.assertEqual(expected, json.loads(output_path.read_text(encoding="utf-8")))

    def test_main_writes_snapshot_and_returns_success(self):
        from tools.write_gptmeai_readonly_snapshot_from_report import main

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "snapshot.json"
            exit_code = main(
                [
                    "--report",
                    str(REPORT_FIXTURE),
                    "--output",
                    str(output_path),
                    "--captured-at",
                    "2026-05-03T00:00:00Z",
                ]
            )

            self.assertEqual(0, exit_code)
            snapshot = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("unavailable", snapshot["status"])
            self.assertTrue(snapshot["metadata"]["dry_run"])
            self.assertTrue(snapshot["metadata"]["read_only"])
            self.assertFalse(snapshot["metadata"]["live_required"])

    def test_tool_does_not_import_live_checker_or_mutation_endpoints(self):
        source = TOOL.read_text(encoding="utf-8")

        for forbidden in FORBIDDEN_TOOL_TEXT:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_local_verification_still_does_not_call_live_checker(self):
        source = LOCAL_VERIFICATION.read_text(encoding="utf-8")

        self.assertNotIn("check_gptmeai_live_readonly.py", source)
        self.assertNotIn("tools\\check_gptmeai_live_readonly.py", source)
        self.assertNotIn("tools/check_gptmeai_live_readonly.py", source)
        self.assertNotIn("write_gptmeai_readonly_snapshot_from_report.py", source)
        self.assertNotIn("tools\\write_gptmeai_readonly_snapshot_from_report.py", source)
        self.assertNotIn("tools/write_gptmeai_readonly_snapshot_from_report.py", source)


if __name__ == "__main__":
    unittest.main()
