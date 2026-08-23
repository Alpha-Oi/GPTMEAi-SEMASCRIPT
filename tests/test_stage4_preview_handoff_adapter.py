import copy
import importlib.util
import unittest
from pathlib import Path

from tools.stage4_preview_handoff_builder import (
    validate_stage4_preview_handoff_envelope,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "stage4_preview_handoff_adapter.py"


ACTION_DOCUMENT = {
    "version": "0.1",
    "source": {
        "system": "SEMASCRIPT",
        "document_id": "sem-adapter-001",
    },
    "intent": {
        "summary": "Build adapter-level preview handoff",
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
        "forbidden_operations": [
            "execute",
            "mutate_gptmeai_storage",
            "mutate_semascript_runtime",
        ],
    },
    "metadata": {
        "fixture": "stage4-preview-handoff-adapter",
    },
}

PLANNER_PREVIEW = {
    "version": "0.1",
    "preview_id": "preview-adapter-001",
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
        "contracts/stage4_preview_handoff_contract.v0.1.json",
        "tools/stage4_preview_handoff_builder.py",
    ]
}


def load_adapter_module():
    if not TOOL.is_file():
        raise AssertionError(f"missing adapter: {TOOL}")
    spec = importlib.util.spec_from_file_location("stage4_preview_handoff_adapter", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage4PreviewHandoffAdapterTests(unittest.TestCase):
    def setUp(self):
        self.module = load_adapter_module()

    def build_envelope(self):
        return self.module.build_stage4_preview_handoff_from_documents(
            copy.deepcopy(ACTION_DOCUMENT),
            copy.deepcopy(PLANNER_PREVIEW),
            source_evidence=copy.deepcopy(SOURCE_EVIDENCE),
        )

    def test_adapter_module_exists_and_imports(self):
        self.assertTrue(TOOL.is_file())
        self.assertTrue(
            hasattr(self.module, "build_stage4_preview_handoff_from_documents")
        )

    def test_adapter_creates_stage4_preview_handoff_envelope(self):
        envelope = self.build_envelope()

        self.assertEqual("STAGE4_PREVIEW_HANDOFF", envelope["handoff_type"])
        self.assertEqual("STAGE4_PREVIEW_HANDOFF", envelope["contract"]["contract_id"])

    def test_returned_envelope_validates_with_existing_builder_validator(self):
        errors = validate_stage4_preview_handoff_envelope(self.build_envelope())

        self.assertEqual([], errors)

    def test_adapter_preserves_safe_flags(self):
        flags = self.build_envelope()["mode_flags"]

        self.assertIs(flags["dry_run"], True)
        self.assertIs(flags["preview_only"], True)
        self.assertIs(flags["execution_allowed"], False)
        self.assertIs(flags["mutation_allowed"], False)
        self.assertIs(flags["requires_human_approval"], True)

    def test_adapter_stops_at_approval_gate_without_runtime_results(self):
        envelope = self.build_envelope()

        self.assertEqual("approval_gate", envelope["stopped_at"])
        self.assertEqual("required", envelope["approval_gate"]["status"])
        self.assertIs(envelope["approval_gate"]["execution_enabled"], False)
        self.assertNotIn("execution_result", envelope)
        self.assertNotIn("dispatch_result", envelope)
        self.assertNotIn("runtime_mutation_result", envelope)

    def test_adapter_does_not_mutate_input_dictionaries(self):
        action_document = copy.deepcopy(ACTION_DOCUMENT)
        planner_preview = copy.deepcopy(PLANNER_PREVIEW)
        action_before = copy.deepcopy(action_document)
        preview_before = copy.deepcopy(planner_preview)

        self.module.build_stage4_preview_handoff_from_documents(
            action_document,
            planner_preview,
            source_evidence=copy.deepcopy(SOURCE_EVIDENCE),
        )

        self.assertEqual(action_before, action_document)
        self.assertEqual(preview_before, planner_preview)

    def test_adapter_output_is_deterministic_for_same_inputs(self):
        first = self.build_envelope()
        second = self.build_envelope()

        self.assertEqual(first, second)

    def test_invalid_semascript_input_type_fails_clearly(self):
        errors = self.module.validate_stage4_preview_handoff_adapter_inputs(
            [], copy.deepcopy(PLANNER_PREVIEW)
        )

        self.assertTrue(any("semascript_action_document must be a dict" in error for error in errors))
        with self.assertRaises(ValueError):
            self.module.build_stage4_preview_handoff_from_documents(
                [], copy.deepcopy(PLANNER_PREVIEW)
            )

    def test_invalid_planner_preview_input_type_fails_clearly(self):
        errors = self.module.validate_stage4_preview_handoff_adapter_inputs(
            copy.deepcopy(ACTION_DOCUMENT), []
        )

        self.assertTrue(any("gptmeai_planner_preview must be a dict" in error for error in errors))
        with self.assertRaises(ValueError):
            self.module.build_stage4_preview_handoff_from_documents(
                copy.deepcopy(ACTION_DOCUMENT), []
            )

    def test_existing_semascript_validation_is_used(self):
        invalid = copy.deepcopy(ACTION_DOCUMENT)
        invalid["safety"]["dry_run_only"] = False

        errors = self.module.validate_stage4_preview_handoff_adapter_inputs(
            invalid, copy.deepcopy(PLANNER_PREVIEW)
        )

        self.assertTrue(
            any("semascript_action_document.safety.dry_run_only" in error for error in errors),
            errors,
        )

    def test_local_planner_preview_validation_is_used(self):
        invalid = copy.deepcopy(PLANNER_PREVIEW)
        invalid["dry_run"] = False

        errors = self.module.validate_stage4_preview_handoff_adapter_inputs(
            copy.deepcopy(ACTION_DOCUMENT), invalid
        )

        self.assertTrue(
            any("gptmeai_planner_preview.dry_run" in error for error in errors),
            errors,
        )

    def test_adapter_includes_composition_diagnostics(self):
        envelope = self.build_envelope()
        diagnostics = " ".join(item["message"] for item in envelope["diagnostics"])
        adapter_evidence = envelope["source_evidence"]["adapter"]

        self.assertIn("Adapter composed", diagnostics)
        self.assertEqual(
            "bridge.semascript_validator.validate_action_document",
            adapter_evidence["semascript_validator"],
        )
        self.assertEqual(
            "local_adapter_required_field_check",
            adapter_evidence["planner_preview_validation"],
        )

    def test_adapter_has_no_runtime_network_write_or_dispatch_primitives(self):
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
