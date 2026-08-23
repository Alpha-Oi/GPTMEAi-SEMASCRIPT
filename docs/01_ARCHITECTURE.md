# Architecture

Target flow:

```text
SEMASCRIPT
  -> parser / AST / validated action document
  -> GPTMEAi-SEMASCRIPT bridge
  -> GPTMEAi planner preview
  -> approval gate
  -> GPTMEAi execution runtime
  -> ledger / snapshot
  -> SEMASCRIPT outcome package
```

## v0.1 Active Flow

```text
SEMASCRIPT action document
  -> bridge.semascript_loader
  -> bridge.semascript_validator
  -> bridge.planner_preview_adapter
  -> bridge.approval_gate
  -> preview-only result
```

The GPTMEAi execution runtime, ledger, snapshot, and SEMASCRIPT outcome package
steps are documented but not active in v0.1.

## Components

- `contracts/`: canonical JSON contract files.
- `bridge/config.py`: standard-library environment configuration.
- `bridge/semascript_loader.py`: JSON file loading with clear errors.
- `bridge/semascript_validator.py`: manual contract validation subset.
- `bridge/gptmeai_client.py`: read-only GPTMEAi status client.
- `bridge/planner_preview_adapter.py`: dry-run preview mapper.
- `bridge/approval_gate.py`: local approval and denial objects.
- `bridge/outcome_mapper.py`: future outcome mapping placeholder.
- `adapters/gptmeai/`: GPTMEAi-facing wrapper exports.
- `adapters/semascript/`: SEMASCRIPT AST normalization.
- `tools/`: verification and source reference utilities.

## Runtime Boundary

No component in v0.1 may call GPTMEAi mutation endpoints or SEMASCRIPT mutation
tools. Any future execution path must be added behind tests, contracts, approval
objects, and explicit task approval.
