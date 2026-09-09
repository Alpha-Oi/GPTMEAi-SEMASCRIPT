<div align="center">

# ◈ GPTMEAi-SEMASCRIPT

### Dry-run integration bridge between GPTMEAi and SEMASCRIPT

**Adapter + contract layer · Event-sourced skeleton · Approval-gated**

[![Tests](https://github.com/Alpha-Oi/GPTMEAi-SEMASCRIPT/actions/workflows/tests.yml/badge.svg)](https://github.com/Alpha-Oi/GPTMEAi-SEMASCRIPT/actions/workflows/tests.yml)
![Status](https://img.shields.io/badge/status-active-22a06b)
![License](https://img.shields.io/badge/license-proprietary-lightgrey)

[Contributing](CONTRIBUTING.md) · [Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md) · [Notice](NOTICE)

</div>

---

GPTMEAi-SEMASCRIPT is a standalone integration bridge between GPTMEAi and
SEMASCRIPT.

It is not a merged runtime, not a replacement for either project, and not a UI
unification effort. GPTMEAi remains the AI OS, host runtime, planner, execution
control plane, ledger, and snapshot layer. SEMASCRIPT remains the semantic
scripting, session, workspace, and lineage layer.

This repository provides the adapter and contract layer between them.

## v0.1 Scope

v0.1 is dry-run only:

1. Load a SEMASCRIPT action document.
2. Validate it against the v0.1 manual safety subset.
3. Normalize or map it into a GPTMEAi planner preview.
4. Require an approval gate before any future execution.
5. Provide a placeholder SEMASCRIPT outcome package mapper.

v0.1 does not call GPTMEAi execution, mutate GPTMEAi state, mutate SEMASCRIPT
state, copy secrets, or merge the projects.

## Basic Usage

Validate and preview the example document:

```powershell
python tools/verify_bridge.py
```

Run unit tests:

```powershell
python -m unittest discover -s tests
```

Collect read-only source references:

```powershell
python tools/collect_source_references.py
```

## Codebase Skeleton

The repository now includes a modular, dependency-free Python skeleton for the
event-driven GPTMEAi-SEMASCRIPT system architecture:

```text
event_store -> state_engine -> snapshot -> cognition
-> risk -> governance -> validation -> system_runtime
```

The skeleton keeps the v0.1 safety boundary intact:

- `event_store/` is the append-only source-of-truth boundary.
- `state_engine/` rebuilds state only by replaying events.
- `snapshot/` creates projection-only state snapshots.
- `cognition/` derives the executable mental model only from snapshots.
- `risk/` classifies proposals before governance or approval.
- `governance/` resolves canonical artifacts and cannot bypass risk results.
- `evolution/` provides deterministic semantic diff and changeset helpers.
- `validation/` checks replay, snapshot, mental-model, and drift consistency.
- `system_runtime/` is a dry-run runtime boundary and performs no real
  execution. The package avoids the forbidden root name `runtime`, which is
  reserved by the project contract for protected runtime data.
- `closed_loop/` wires the integrated closed evolution loop.
- `artifact_system/` reads ARTIFACT_INDEX metadata, lineage, and graph hooks.
- `bridge/` keeps SEMASCRIPT contract validation, intent parsing, and dry-run
  preview generation.

Skeleton verification:

```powershell
python -B -m unittest tests.test_system_skeleton
```

## Local Verification

Preferred pre-handoff local smoke:

```powershell
python -B tools\run_local_verification.py
```

This runs root cleanliness, schema consistency, the full unittest suite,
dry-run bridge smoke, and source reference refresh.

Optional live read-only GPTMEAi status checks are available through
`python -B tools\check_gptmeai_live_readonly.py`.

Schema or compatibility changes must pass schema consistency and local
verification before handoff.

Before handoff, follow `docs/06_HANDOFF_CHECKLIST.md`.

## Project Continuity

For roadmap-driven work, see `docs/03_ROADMAP.md`. Before handoff, follow
`docs/06_HANDOFF_CHECKLIST.md` and run:

```powershell
python -B tools\run_local_verification.py
```

## Configuration

Copy `.env.example` values into your own environment if needed. v0.1 keeps
bridge behavior dry-run even when configuration is present.

```text
GPTMEAI_BASE_URL=http://127.0.0.1:8010
GPTMEAI_SEMASCRIPT_DRY_RUN=true
GPTMEAI_SEMASCRIPT_REQUIRE_APPROVAL=true
```

## Roadmap

- v0.1: dry-run contracts, validator, planner preview, local approval objects.
- v0.2: richer AST normalization and contract compatibility checks.
- v0.3: approved execution handoff design, still gated and auditable.
- v1.0: execution-enabled bridge only after explicit approval, tests, and
  mutation boundaries.
