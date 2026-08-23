import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = (
    ROOT
    / "docs"
    / "semantic_dictionaries"
    / "system_thinking_dictionary_v1_ru.md"
)


REQUIRED_TEXT = (
    "# System Thinking Dictionary v1 RU",
    "Status: read-only reference",
    "Source status:",
    "Allowed use:",
    "Forbidden use:",
    "Guard questions:",
    "No runtime behavior changes",
    "No API changes",
    "No planner or dispatch changes",
    "No Stage 4 builder or adapter behavior changes",
    "No execution calls",
    "No live runtime startup",
    "No memory, storage, session, workspace, lineage, ledger, or database mutation",
    "No source project edits",
    "No dependency, environment, package, or lockfile changes",
)

FORBIDDEN_TEXT = (
    "runtime integration is enabled",
    "planner decision authority",
    "dispatch is enabled",
    "execution is enabled",
    "source project mutation is allowed",
    "automatic decision-making is enabled",
    "install dependencies",
    "exact quote from jacque fresco",
)


class SemanticDictionariesGuardTests(unittest.TestCase):
    def test_system_thinking_dictionary_exists(self):
        self.assertTrue(DICTIONARY.is_file(), f"missing dictionary: {DICTIONARY}")

    def test_system_thinking_dictionary_preserves_required_boundaries(self):
        content = DICTIONARY.read_text(encoding="utf-8")

        missing = [text for text in REQUIRED_TEXT if text not in content]

        self.assertEqual([], missing)

    def test_system_thinking_dictionary_does_not_authorize_runtime_behavior(self):
        content = DICTIONARY.read_text(encoding="utf-8").lower()

        for forbidden in FORBIDDEN_TEXT:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)

    def test_system_thinking_dictionary_uses_expected_entry_shape(self):
        content = DICTIONARY.read_text(encoding="utf-8")

        self.assertIn("## Dictionary entries", content)
        self.assertIn("### environment_to_behavior", content)
        self.assertIn("Engineering meaning:", content)
        self.assertIn("Project use:", content)
        self.assertIn("Risk:", content)
        self.assertIn("Guard question:", content)


if __name__ == "__main__":
    unittest.main()
