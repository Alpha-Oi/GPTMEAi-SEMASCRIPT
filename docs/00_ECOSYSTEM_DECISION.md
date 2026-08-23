# Ecosystem Decision

GPTMEAi remains the AI OS, host runtime, control plane, planner, execution
runtime, ledger, and snapshot system.

SEMASCRIPT remains the semantic scripting, session, workspace, and lineage
layer.

GPTMEAi-SEMASCRIPT is the adapter and contract bridge between the two systems.
It exists to translate validated SEMASCRIPT intent into GPTMEAi planner previews
and, in future versions, translate GPTMEAi results back into SEMASCRIPT outcome
packages.

## Non-Goals

- Do not merge runtimes.
- Do not merge UIs.
- Do not create a monolith.
- Do not destructively synchronize source projects.
- Do not copy source project internals into this bridge.

## v0.1 Decision

v0.1 is dry-run only. It creates contracts, examples, validation, preview
mapping, local approval objects, and source reference manifests.
