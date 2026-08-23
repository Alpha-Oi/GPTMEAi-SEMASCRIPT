# Handoff Checklist

## Purpose

This checklist is for future Codex tasks and handoffs inside
`D:\GPTMEAi-SEMASCRIPT`.

## Canonical Workspace

`D:\GPTMEAi-SEMASCRIPT` is the canonical workspace.

## Source Project Boundaries

These source projects are read-only unless a task explicitly says otherwise:

- `D:\Development GPTMEAi`
- `D:\SEMASCRIPT\SEMASCRIPT_current_bundle`

## v0.1 Safety Boundary

v0.1 remains:

- dry-run only
- preview only
- no execution
- no memory, storage, ledger, or runtime mutation

## Required Pre-Handoff Commands

Run these checks before handoff:

```powershell
python -B tools\check_root_cleanliness.py
python -B tools\check_schema_consistency.py
python -B -m unittest discover -s tests
python -B tools\verify_bridge.py
python -B tools\collect_source_references.py
python -B tools\run_local_verification.py
```

Preferred single command:

```powershell
python -B tools\run_local_verification.py
```

## Required Success Signals

- `ROOT_CLEANLINESS=OK`
- `SCHEMA_CONSISTENCY=OK`
- `VERIFY_BRIDGE=OK`
- `LOCAL_VERIFICATION=OK`
- `MISSING_COUNT=0`
- full unittest `OK`

## Optional Live Read-Only Checks

After required local verification passes, maintainers may optionally run:

```powershell
python -B tools\check_gptmeai_live_readonly.py
```

This check is read-only and only targets `/health`, `/planner/status`, and
`/execution/status`.

It must not gate v0.1 handoff. GPTMEAi runtime unavailability is acceptable for
v0.1 as long as required local verification passes.

An already-saved live-readonly report may optionally be converted into the
canonical readonly status snapshot by the bridge report adapter. That conversion
does not perform network calls and must not be required for v0.1 handoff.

Optional snapshot artifact command:

```powershell
python -B tools\write_gptmeai_readonly_snapshot_from_report.py
```

This writes `reports/codex/GPTMEAI_READONLY_STATUS_SNAPSHOT_FROM_LIVE_REPORT.json`
from an existing saved report and must not be added to the required local
verification wrapper.

## Report Placement

All Codex operational reports must be written to `reports/codex/`.
Do not write reports into the project root.

## Final Codex Response

Codex should report only:

- green/red status
- main task report path
- verification summary

Do not surface every updated project file unless verification failed.

## Stop Conditions

Stop the task if any of these occur:

- source project mutation detected
- execution endpoint added
- dependency install attempted
- root report generated
- schema consistency failed
- root cleanliness failed
- local verification failed
- secrets, runtime, storage, memory, or logs copied

## Next-Step Discipline

Future tasks should be bounded slices and must not mix feature work with broad
cleanup.
