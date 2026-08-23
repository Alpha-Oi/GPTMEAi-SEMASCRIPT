import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "10_STAGE4_FUNCTIONAL_INTEGRATION_DESIGN.md"


REQUIRED_TEXT = (
    "STAGE4_PREVIEW_HANDOFF_DESIGN_ONLY",
    "SEMASCRIPT action document -> validate -> normalize -> GPTMEAi planner preview handoff -> approval gate",
    "dry-run",
    "preview-only",
    "no execution",
    "Required Source Evidence Before Implementation",
    "Mutation Boundaries",
    "Approval Gates",
    "Rollback Plan",
    "Verification Gates",
    "Non-goals",
    "no `execute()` method",
    "no runtime mutation",
    "no source project edits",
    "no GPTMEAi memory/storage/ledger mutation",
    "no SEMASCRIPT runtime/session/workspace/lineage mutation",
)


class Stage4DesignGuardTests(unittest.TestCase):
    def test_stage4_design_doc_exists(self):
        self.assertTrue(DOC.is_file(), f"missing design document: {DOC}")

    def test_stage4_design_doc_preserves_required_boundaries(self):
        content = DOC.read_text(encoding="utf-8")

        missing = [text for text in REQUIRED_TEXT if text not in content]

        self.assertEqual([], missing)

    def test_stage4_design_doc_does_not_authorize_implementation(self):
        content = DOC.read_text(encoding="utf-8").lower()

        self.assertNotIn("stage 4 implementation is approved", content)
        self.assertNotIn("execution is enabled", content)
        self.assertNotIn("live runtime startup is required", content)


if __name__ == "__main__":
    unittest.main()
