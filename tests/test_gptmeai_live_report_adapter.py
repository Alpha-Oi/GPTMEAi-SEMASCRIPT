import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "compatibility"
ADAPTER = ROOT / "bridge" / "gptmeai_live_report_adapter.py"
SCHEMA = ROOT / "contracts" / "gptmeai_readonly_status_snapshot.schema.json"
LOCAL_VERIFICATION = ROOT / "tools" / "run_local_verification.py"
UNAVAILABLE_REPORT = FIXTURES / "gptmeai_live_readonly_report.unavailable.md"
UNAVAILABLE_EXPECTED = (
    FIXTURES / "gptmeai_live_readonly_snapshot_from_report.expected.json"
)
FORBIDDEN_TEXT = (
    "GPTMEAiReadOnlyClient",
    "check_gptmeai_live_readonly",
    "/execute",
    "/execution/run",
    "/memory/add",
    "/memory/delete",
    "/ledger/write",
    ".execute(",
)


def synthetic_report(health_available=True, planner_available=True, execution_available=True):
    endpoint_specs = (
        ("/health", health_available, {"status": "ok", "service": "gptmeai"}),
        ("/planner/status", planner_available, {"planner": "ready", "queue_depth": 0}),
        (
            "/execution/status",
            execution_available,
            {"execution": "idle", "active_runs": 0},
        ),
    )
    lines = [
        "# GPTMEAI_LIVE_READONLY_STATUS_REPORT.md",
        "",
        "- Generated: `2026-05-03T00:00:00Z`",
        "- Status: `OK`",
        "",
        "## Endpoints",
        "",
    ]
    for endpoint, available, payload in endpoint_specs:
        body = payload if available else {}
        top_level_keys = ", ".join(sorted(body.keys()))
        lines.extend(
            [
                f"### `{endpoint}`",
                "",
                f"- Available: `{available}`",
                "- HTTP status: `200`" if available else "- HTTP status: `None`",
                f"- OK: `{available}`",
                "- Malformed: `False`",
                f"- Top-level keys: `{top_level_keys}`",
                "",
                "```json",
                json.dumps(body, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


class GPTMEAiLiveReadonlyReportAdapterTests(unittest.TestCase):
    def test_adapter_file_exists(self):
        self.assertTrue(ADAPTER.is_file())

    def test_unavailable_report_converts_to_expected_snapshot(self):
        from bridge.gptmeai_live_report_adapter import (
            snapshot_from_live_readonly_report_text,
        )

        report_text = UNAVAILABLE_REPORT.read_text(encoding="utf-8")
        expected = json.loads(UNAVAILABLE_EXPECTED.read_text(encoding="utf-8"))

        snapshot = snapshot_from_live_readonly_report_text(
            report_text,
            captured_at="2026-05-03T00:00:00Z",
        )

        self.assertEqual("unavailable", snapshot["status"])
        self.assertEqual(expected, snapshot)

    def test_mixed_report_converts_to_degraded_snapshot(self):
        from bridge.gptmeai_live_report_adapter import (
            snapshot_from_live_readonly_report_text,
        )

        snapshot = snapshot_from_live_readonly_report_text(
            synthetic_report(execution_available=False),
            captured_at="2026-05-03T00:00:00Z",
        )

        self.assertEqual("degraded", snapshot["status"])
        self.assertTrue(snapshot["health"]["available"])
        self.assertTrue(snapshot["planner"]["available"])
        self.assertFalse(snapshot["execution"]["available"])

    def test_all_available_report_converts_to_ok_snapshot(self):
        from bridge.gptmeai_live_report_adapter import (
            snapshot_from_live_readonly_report_text,
        )

        snapshot = snapshot_from_live_readonly_report_text(
            synthetic_report(),
            captured_at="2026-05-03T00:00:00Z",
        )

        self.assertEqual("ok", snapshot["status"])
        self.assertTrue(snapshot["health"]["available"])
        self.assertTrue(snapshot["planner"]["available"])
        self.assertTrue(snapshot["execution"]["available"])

    def test_snapshot_contains_required_schema_top_level_fields(self):
        from bridge.gptmeai_live_report_adapter import (
            snapshot_from_live_readonly_report_text,
        )

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        snapshot = snapshot_from_live_readonly_report_text(
            synthetic_report(),
            captured_at="2026-05-03T00:00:00Z",
        )

        self.assertTrue(set(schema["required"]).issubset(snapshot.keys()))

    def test_snapshot_metadata_is_dry_run_read_only_and_live_optional(self):
        from bridge.gptmeai_live_report_adapter import (
            snapshot_from_live_readonly_report_text,
        )

        snapshot = snapshot_from_live_readonly_report_text(
            synthetic_report(),
            captured_at="2026-05-03T00:00:00Z",
        )

        self.assertTrue(snapshot["metadata"]["dry_run"])
        self.assertTrue(snapshot["metadata"]["read_only"])
        self.assertFalse(snapshot["metadata"]["live_required"])

    def test_adapter_does_not_import_live_checker_or_mutation_endpoints(self):
        source = ADAPTER.read_text(encoding="utf-8")

        for forbidden in FORBIDDEN_TEXT:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_local_verification_still_does_not_call_live_checker(self):
        source = LOCAL_VERIFICATION.read_text(encoding="utf-8")

        self.assertNotIn("check_gptmeai_live_readonly.py", source)
        self.assertNotIn("tools\\check_gptmeai_live_readonly.py", source)
        self.assertNotIn("tools/check_gptmeai_live_readonly.py", source)


if __name__ == "__main__":
    unittest.main()
