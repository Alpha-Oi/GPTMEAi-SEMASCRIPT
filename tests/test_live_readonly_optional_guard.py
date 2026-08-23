import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIVE_CHECKER = ROOT / "tools" / "check_gptmeai_live_readonly.py"
LOCAL_VERIFICATION = ROOT / "tools" / "run_local_verification.py"
DOCS_WITH_OPTIONAL_MENTIONS = (
    ROOT / "README.md",
    ROOT / "docs" / "04_VERIFICATION.md",
    ROOT / "docs" / "03_ROADMAP.md",
)
FORBIDDEN_WRAPPER_REFERENCES = (
    "check_gptmeai_live_readonly.py",
    "tools\\check_gptmeai_live_readonly.py",
    "tools/check_gptmeai_live_readonly.py",
)


class LiveReadonlyOptionalGuardTests(unittest.TestCase):
    def test_live_readonly_checker_exists(self):
        self.assertTrue(LIVE_CHECKER.is_file())

    def test_local_verification_wrapper_exists(self):
        self.assertTrue(LOCAL_VERIFICATION.is_file())

    def test_local_verification_does_not_call_live_readonly_checker(self):
        source = LOCAL_VERIFICATION.read_text(encoding="utf-8")

        for reference in FORBIDDEN_WRAPPER_REFERENCES:
            with self.subTest(reference=reference):
                self.assertNotIn(reference, source)

    def test_docs_mentions_are_optional_only(self):
        for doc_path in DOCS_WITH_OPTIONAL_MENTIONS:
            with self.subTest(doc_path=doc_path.name):
                text = doc_path.read_text(encoding="utf-8").lower()
                if "check_gptmeai_live_readonly.py" not in text:
                    continue
                self.assertIn("optional", text)
                self.assertNotIn("required live read-only", text)
                self.assertNotIn("must run live read-only", text)
                self.assertNotIn("required for v0.1", text)


if __name__ == "__main__":
    unittest.main()
