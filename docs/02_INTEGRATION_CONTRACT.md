# Integration Contract

Contracts in `contracts/` define the integration surface.

The v0.1 compatibility matrix is documented in
`docs/05_CONTRACT_COMPATIBILITY_MATRIX.md` and mirrored as machine-readable
JSON in `contracts/compatibility_matrix.v0.1.json`.

## Contract Maintenance Rule

Any change to files under `contracts/*.schema.json` or
`contracts/compatibility_matrix.v0.1.json` must also update the matching
contract documentation and compatibility matrix.

Before handoff, run:

```powershell
python -B tools\check_schema_consistency.py
python -B tools\run_local_verification.py
```

A change is not complete if schemas, matrix, and docs disagree.

## SEMASCRIPT Action Document

Canonical input from SEMASCRIPT or a SEMASCRIPT AST adapter.

Required fields:

- `version`
- `source`
- `intent`
- `actions`
- `constraints`
- `safety`
- `metadata`

v0.1 requires `source.system` to be `SEMASCRIPT`, at least one action, and safety
flags `dry_run_only: true` and `requires_approval: true`.

## GPTMEAi Planner Preview

Dry-run output that can be reviewed before any future execution.

Required fields:

- `version`
- `preview_id`
- `status`
- `mapped_actions`
- `required_approvals`
- `risks`
- `dry_run`
- `metadata`

v0.1 always emits `dry_run: true` and at least one approval requirement.

## Execution Approval

Local approval object for future execution handoff design. In v0.1, approvals
are records only and do not enable execution.

Required fields:

- `approval_id`
- `preview_id`
- `approved`
- `approved_by`
- `scope`
- `expires_at`
- `metadata`

## Adapter Error Model

Structured error model for validation, adapter, client, and mapping failures.

Required fields:

- `error_code`
- `message`
- `severity`
- `source`
- `retryable`
- `details`

## GPTMEAi Readonly Status Snapshot

v0.2-prep read-only contract for summarizing GPTMEAi `/health`,
`/planner/status`, and `/execution/status` payloads into a canonical snapshot.
It does not require live GPTMEAi availability and does not change the v0.1
dry-run boundary.

An optional live-readonly report adapter may convert an already-saved
`reports/codex/GPTMEAI_LIVE_READONLY_STATUS_REPORT.md` file into this canonical
snapshot shape. The adapter performs no network calls and does not gate v0.1
local verification.

## Outcome Package

Future SEMASCRIPT-facing result package. v0.1 only returns a placeholder with
`dry_run: true` and does not represent real execution output.

## Mutation Rules

- GPTMEAi source project is read-only.
- SEMASCRIPT source project is read-only.
- GPTMEAi memory, storage, runtime, and ledger must not be mutated.
- SEMASCRIPT runtime, sessions, workspaces, and lineage must not be mutated.
- No execution path is allowed in v0.1.

## Security Rules

- Do not copy `.env` files or secrets.
- Do not expose tokens, credentials, keys, certificates, private data, runtime
  databases, logs, storage, memory, or user data.
- Use standard-library clients and explicit allowlists.
- Treat source project files as read-only evidence.
