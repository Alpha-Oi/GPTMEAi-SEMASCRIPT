import ast
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "check_gptmeai_live_readonly.py"
ALLOWED_ENDPOINTS = {
    "/health",
    "/planner/status",
    "/execution/status",
}
FORBIDDEN_ENDPOINTS = (
    "/execute",
    "/memory/add",
    "/memory/delete",
    "/execution/run",
    "/ledger/write",
)
STDLIB_IMPORT_ROOTS = {
    "argparse",
    "datetime",
    "json",
    "os",
    "pathlib",
    "sys",
    "time",
    "urllib",
}


def load_tool_module():
    if not TOOL.is_file():
        raise AssertionError("check_gptmeai_live_readonly.py is missing")
    spec = importlib.util.spec_from_file_location("check_gptmeai_live_readonly", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GPTMEAiLiveReadonlyCheckTests(unittest.TestCase):
    def test_tool_exists(self):
        self.assertTrue(TOOL.is_file())

    def test_tool_only_targets_allowed_read_only_endpoints(self):
        module = load_tool_module()

        self.assertEqual(ALLOWED_ENDPOINTS, set(module.ALLOWED_ENDPOINTS))

    def test_tool_does_not_contain_mutation_endpoint_strings(self):
        source = TOOL.read_text(encoding="utf-8")

        for endpoint in FORBIDDEN_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                self.assertNotIn(endpoint, source)

    def test_report_path_is_under_reports_codex(self):
        module = load_tool_module()
        path = module.report_path(ROOT)

        self.assertEqual(
            ROOT / "reports" / "codex" / "GPTMEAI_LIVE_READONLY_STATUS_REPORT.md",
            path,
        )
        self.assertNotEqual(ROOT / "GPTMEAI_LIVE_READONLY_STATUS_REPORT.md", path)

    def test_non_strict_unavailable_mode_exits_zero(self):
        module = load_tool_module()
        result = module.evaluate_results(
            [{"endpoint": "/health", "available": False, "error": "offline"}],
            strict=False,
        )

        self.assertEqual("UNAVAILABLE", result["status"])
        self.assertEqual(0, result["exit_code"])

    def test_strict_unavailable_mode_exits_nonzero(self):
        module = load_tool_module()
        result = module.evaluate_results(
            [{"endpoint": "/health", "available": False, "error": "offline"}],
            strict=True,
        )

        self.assertEqual("UNAVAILABLE", result["status"])
        self.assertNotEqual(0, result["exit_code"])

    def test_tool_uses_standard_library_only(self):
        source_tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(source_tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        self.assertTrue(imported_roots.issubset(STDLIB_IMPORT_ROOTS), imported_roots)


if __name__ == "__main__":
    unittest.main()
