import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "stage4_preview_handoff_status.py"
WATCHED_PATHS = (
    ROOT,
    ROOT / "tools",
    ROOT / "tests",
    ROOT / "reports" / "codex",
    ROOT / "source_references",
)
EXPECTED_LINES = (
    "STAGE4_PREVIEW_HANDOFF_STATUS=OK",
    "HANDOFF_TYPE=STAGE4_PREVIEW_HANDOFF",
    "DRY_RUN=True",
    "PREVIEW_ONLY=True",
    "EXECUTION_ALLOWED=False",
    "MUTATION_ALLOWED=False",
    "REQUIRES_HUMAN_APPROVAL=True",
    "APPROVAL_GATE=required",
    "RUNTIME_CALLS=none",
    "SOURCE_PROJECT_MUTATION=none",
)


def load_status_module():
    if not TOOL.is_file():
        raise AssertionError(f"missing status CLI: {TOOL}")
    spec = importlib.util.spec_from_file_location("stage4_preview_handoff_status", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tracked_files(path):
    if not path.exists():
        return {}
    if path.is_file():
        paths = (path,)
    else:
        paths = (
            item
            for item in path.rglob("*")
            if item.is_file()
            and "__pycache__" not in item.parts
            and item.suffix != ".pyc"
        )
    return {
        str(item.relative_to(ROOT)): (item.stat().st_size, item.stat().st_mtime_ns)
        for item in paths
    }


def _snapshot_watched_paths():
    return {str(path.relative_to(ROOT)): _tracked_files(path) for path in WATCHED_PATHS}


class Stage4PreviewHandoffStatusCliTests(unittest.TestCase):
    def test_status_cli_module_exists_and_imports(self):
        module = load_status_module()

        self.assertTrue(TOOL.is_file())
        self.assertTrue(hasattr(module, "main"))

    def test_status_cli_runs_and_prints_safety_markers(self):
        before = _snapshot_watched_paths()

        completed = subprocess.run(
            [sys.executable, "-B", str(TOOL)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        after = _snapshot_watched_paths()
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        for line in EXPECTED_LINES:
            with self.subTest(line=line):
                self.assertIn(line, completed.stdout)
        self.assertIn("FIXTURE_SOURCE=embedded", completed.stdout)
        self.assertEqual(before, after)

    def test_status_cli_source_has_no_runtime_network_write_or_dispatch_primitives(self):
        self.assertTrue(TOOL.is_file(), f"missing status CLI: {TOOL}")
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
            "dispatch(",
            "d:\\development gptmeai",
            "d:\\semascript\\semascript_current_bundle",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
