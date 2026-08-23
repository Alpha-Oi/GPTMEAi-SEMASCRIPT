import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "stage4_preview_handoff_builder.py"


ACTION_DOCUMENT = {
    "version": "0.1",
    "source": {
        "system": "SEMASCRIPT",
        "document_id": "sem-test-001",
    },
    "intent": {
        "summary": "Preview a local dry-run handoff",
    },
    "actions": [
        {
            "id": "action-1",
            "type": "inspect",
            "description": "Inspect local bridge state without mutation",
            "inputs": {"target": "bridge"},
            "expected_output": "preview",
        }
    ],
    "constraints": {
        "dry_run": True,
    },
    "safety": {
        "dry_run_only": True,
        "requires_approval": True,
    },
    "metadata": {
        "fixture": "stage4-preview-handoff",
    },
}

PLANNER_PREVIEW = {
    "version": "0.1",
    "preview_id": "preview-test-001",
    "status": "preview",
    "mapped_actions": [
        {
            "source_action_id": "action-1",
            "operation": "inspect",
            "planner_step": "Inspect local bridge state without mutation",
        }
    ],
    "required_approvals": [
        {
            "type": "execution_approval",
            "required": True,
        }
    ],
    "risks": [
        {
            "level": "low",
            "message": "dry-run preview only",
        }
    ],
    "dry_run": True,
    "metadata": {
        "source_system": "SEMASCRIPT",
    },
}

SOURCE_EVIDENCE = {
    "files": [
        "contracts/semascript_action_document.schema.json",
        "contracts/gptmeai_planner_preview.schema.json",
        "contracts/stage4_preview_handoff_contract.v0.1.json",
    ]
}


def load_builder_module():
    if not TOOL.is_file():
        raise AssertionError(f"missing builder: {TOOL}")
    spec = importlib.util.spec_from_file_location("stage4_preview_handoff_builder", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage4PreviewHandoffBuilderTests(unittest.TestCase):
    def setUp(self):
        self.module = load_builder_module()

    def build_envelope(self):
        return self.module.build_stage4_preview_handoff(
            copy.deepcopy(ACTION_DOCUMENT),
            copy.deepcopy(PLANNER_PREVIEW),
            source_evidence=copy.deepcopy(SOURCE_EVIDENCE),
        )

    def test_builder_module_exists_and_imports(self):
        self.assertTrue(TOOL.is_file())
        self.assertTrue(hasattr(self.module, "build_stage4_preview_handoff"))

    def test_builder_creates_stage4_preview_handoff_envelope(self):
        envelope = self.build_envelope()

        self.assertEqual("STAGE4_PREVIEW_HANDOFF", envelope["handoff_type"])
        self.assertEqual("STAGE4_PREVIEW_HANDOFF", envelope["contract"]["contract_id"])
        self.assertEqual("0.1", envelope["contract"]["version"])

    def test_generated_envelope_validates_with_no_errors(self):
        errors = self.module.validate_stage4_preview_handoff_envelope(self.build_envelope())

        self.assertEqual([], errors)

    def test_assert_accepts_valid_envelope(self):
        self.module.assert_stage4_preview_handoff_envelope_valid(self.build_envelope())

    def test_generated_envelope_has_safe_flags(self):
        flags = self.build_envelope()["mode_flags"]

        self.assertIs(flags["dry_run"], True)
        self.assertIs(flags["preview_only"], True)
        self.assertIs(flags["execution_allowed"], False)
        self.assertIs(flags["mutation_allowed"], False)
        self.assertIs(flags["requires_human_approval"], True)

    def test_generated_envelope_stops_at_approval_gate_without_runtime_results(self):
        envelope = self.build_envelope()

        self.assertEqual("approval_gate", envelope["stopped_at"])
        self.assertEqual("required", envelope["approval_gate"]["status"])
        self.assertIs(envelope["approval_gate"]["execution_enabled"], False)
        self.assertNotIn("execution_result", envelope)
        self.assertNotIn("dispatch_result", envelope)
        self.assertNotIn("runtime_mutation_result", envelope)

    def test_generated_envelope_includes_required_sections(self):
        envelope = self.build_envelope()

        for key in (
            "source_evidence",
            "normalized_action_document",
            "planner_preview_handoff",
            "diagnostics",
            "mutation_boundaries",
            "explicit_non_goals",
        ):
            self.assertIn(key, envelope)

    def test_builder_does_not_mutate_input_dictionaries(self):
        action_document = copy.deepcopy(ACTION_DOCUMENT)
        planner_preview = copy.deepcopy(PLANNER_PREVIEW)
        action_before = copy.deepcopy(action_document)
        preview_before = copy.deepcopy(planner_preview)

        self.module.build_stage4_preview_handoff(
            action_document,
            planner_preview,
            source_evidence=copy.deepcopy(SOURCE_EVIDENCE),
        )

        self.assertEqual(action_before, action_document)
        self.assertEqual(preview_before, planner_preview)

    def test_builder_output_is_deterministic_for_same_inputs(self):
        first = self.build_envelope()
        second = self.build_envelope()

        self.assertEqual(first, second)

    def test_invalid_input_types_raise_clear_error(self):
        with self.assertRaises(TypeError):
            self.module.build_stage4_preview_handoff([], copy.deepcopy(PLANNER_PREVIEW))

        with self.assertRaises(TypeError):
            self.module.build_stage4_preview_handoff(copy.deepcopy(ACTION_DOCUMENT), [])

    def test_unsafe_envelope_variants_fail_validation(self):
        unsafe_cases = (
            ("execution_allowed", True),
            ("mutation_allowed", True),
            ("requires_human_approval", False),
        )
        for flag, value in unsafe_cases:
            with self.subTest(flag=flag):
                envelope = self.build_envelope()
                envelope["mode_flags"][flag] = value

                errors = self.module.validate_stage4_preview_handoff_envelope(envelope)

                self.assertTrue(any(f"mode_flags.{flag}" in error for error in errors), errors)

    def test_missing_required_sections_fail_validation(self):
        for section in self.module.REQUIRED_ENVELOPE_SECTIONS:
            with self.subTest(section=section):
                envelope = self.build_envelope()
                envelope.pop(section)

                errors = self.module.validate_stage4_preview_handoff_envelope(envelope)

                self.assertTrue(any(section in error for error in errors), errors)

    def test_builder_has_no_runtime_network_write_or_dispatch_primitives(self):
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
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
