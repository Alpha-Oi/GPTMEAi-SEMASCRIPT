# Roadmap

## v0.1 Dry-Run Bridge

- Local project contract.
- Canonical JSON contracts.
- SEMASCRIPT action document loader and validator.
- GPTMEAi read-only status client.
- Planner preview adapter.
- Local approval gate objects.
- Placeholder outcome mapper.
- Examples, fixtures, and unittest coverage.
- Read-only source reference manifest.

## v0.2 Contract Hardening

- Broader SEMASCRIPT AST normalization.
- Contract compatibility tests against selected source project interfaces.
- More complete error model usage across tools.
- Better preview risk classification.
- Optional live read-only GPTMEAi status checks, without execution.
- Read-only GPTMEAi status snapshot contract for future bridge consumers.

## v0.3 Approved Execution Design

- Design-only execution handoff.
- Approval object persistence contract.
- Ledger/snapshot mapping contract.
- Rollback and audit requirements.

## Roadmap Handoff Gate

Before any roadmap item is considered complete, follow
`docs/06_HANDOFF_CHECKLIST.md`.

At minimum, the preferred pre-handoff command is:

```powershell
python -B tools\run_local_verification.py
```

Roadmap work is not complete if root cleanliness, schema consistency, tests,
dry-run bridge verification, or source reference collection fail.

## v1.0 Execution-Enabled Bridge

Execution may be considered only after explicit approval, current source
evidence, hardened contracts, tests, security review, and verified mutation
boundaries.
