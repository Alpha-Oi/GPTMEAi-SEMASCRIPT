import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "compatibility"
SCHEMA = ROOT / "contracts" / "gptmeai_readonly_status_snapshot.schema.json"
EXPECTED = FIXTURES / "gptmeai_readonly_status_snapshot.expected.json"
MAPPER = ROOT / "bridge" / "gptmeai_status_snapshot.py"
FORBIDDEN_TEXT = (
    "/execute",
    "/memory/add",
    "/memory/delete",
    "/execution/run",
    "/ledger/write",
    ".execute(",
)


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class GPTMEAiReadonlyStatusSnapshotTests(unittest.TestCase):
    def test_schema_file_exists_and_is_valid_json(self):
        self.assertTrue(SCHEMA.is_file())
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual("object", schema["type"])
        self.assertTrue(
            {
                "version",
                "source",
                "status",
                "captured_at",
                "health",
                "planner",
                "execution",
                "metadata",
            }.issubset(set(schema["required"]))
        )

    def test_build_status_snapshot_returns_required_top_level_fields(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        snapshot = build_status_snapshot(captured_at="2026-05-02T00:00:00Z")

        self.assertTrue(
            {
                "version",
                "source",
                "status",
                "captured_at",
                "health",
                "planner",
                "execution",
                "metadata",
            }.issubset(snapshot.keys())
        )

    def test_full_fixture_input_produces_ok_snapshot(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        health = load_fixture("gptmeai_health.sample.json")
        planner = load_fixture("gptmeai_planner_status.sample.json")
        execution = load_fixture("gptmeai_execution_status.sample.json")
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

        snapshot = build_status_snapshot(
            health=health,
            planner=planner,
            execution=execution,
            captured_at="2026-05-02T00:00:00Z",
        )

        self.assertEqual("ok", snapshot["status"])
        self.assertEqual(expected, snapshot)

    def test_missing_one_section_produces_degraded_snapshot(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        snapshot = build_status_snapshot(
            health=load_fixture("gptmeai_health.sample.json"),
            planner=load_fixture("gptmeai_planner_status.sample.json"),
            execution=None,
            captured_at="2026-05-02T00:00:00Z",
        )

        self.assertEqual("degraded", snapshot["status"])
        self.assertFalse(snapshot["execution"]["available"])

    def test_missing_all_sections_produces_unavailable_snapshot(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        snapshot = build_status_snapshot(captured_at="2026-05-02T00:00:00Z")

        self.assertEqual("unavailable", snapshot["status"])
        self.assertFalse(snapshot["health"]["available"])
        self.assertFalse(snapshot["planner"]["available"])
        self.assertFalse(snapshot["execution"]["available"])

    def test_snapshot_metadata_is_dry_run_read_only_and_live_optional(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        snapshot = build_status_snapshot(captured_at="2026-05-02T00:00:00Z")

        self.assertTrue(snapshot["metadata"]["dry_run"])
        self.assertTrue(snapshot["metadata"]["read_only"])
        self.assertFalse(snapshot["metadata"]["live_required"])

    def test_inputs_are_not_mutated(self):
        from bridge.gptmeai_status_snapshot import build_status_snapshot

        health = load_fixture("gptmeai_health.sample.json")
        planner = load_fixture("gptmeai_planner_status.sample.json")
        execution = load_fixture("gptmeai_execution_status.sample.json")
        original = (copy.deepcopy(health), copy.deepcopy(planner), copy.deepcopy(execution))

        build_status_snapshot(
            health=health,
            planner=planner,
            execution=execution,
            captured_at="2026-05-02T00:00:00Z",
        )

        self.assertEqual(original, (health, planner, execution))

    def test_mapper_does_not_contain_mutation_or_execution_endpoint_strings(self):
        self.assertTrue(MAPPER.is_file())
        source = MAPPER.read_text(encoding="utf-8")

        for forbidden in FORBIDDEN_TEXT:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_schema_consistency_still_passes(self):
        from tools.check_schema_consistency import check_consistency

        result = check_consistency(ROOT)

        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
