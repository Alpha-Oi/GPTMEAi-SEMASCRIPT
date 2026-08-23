import json
import unittest
from pathlib import Path

from bridge.approval_gate import require_approval
from bridge.gptmeai_client import GPTMEAiReadOnlyClient
from bridge.planner_preview_adapter import map_semascript_to_planner_preview


ROOT = Path(__file__).resolve().parents[1]


class DryRunAdapterTests(unittest.TestCase):
    def load_valid_document(self):
        return json.loads(
            (ROOT / "tests" / "fixtures" / "semascript_action_document.valid.json").read_text(
                encoding="utf-8"
            )
        )

    def test_preview_is_dry_run(self):
        preview = map_semascript_to_planner_preview(self.load_valid_document())

        self.assertTrue(preview["dry_run"])
        self.assertEqual("preview", preview["status"])

    def test_preview_requires_approval(self):
        preview = map_semascript_to_planner_preview(self.load_valid_document())

        self.assertTrue(require_approval(preview))
        self.assertGreaterEqual(len(preview["required_approvals"]), 1)

    def test_gptmeai_client_has_no_execution_method_in_v01(self):
        client = GPTMEAiReadOnlyClient("http://127.0.0.1:8010", timeout=0.1)

        self.assertFalse(hasattr(client, "execute"))


if __name__ == "__main__":
    unittest.main()
