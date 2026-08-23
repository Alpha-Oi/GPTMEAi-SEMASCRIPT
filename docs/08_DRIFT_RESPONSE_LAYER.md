# Drift Response & Governed Correction Layer

`drift_response/` evaluates drift reports from `live_sync/` and produces
governed correction proposals.

It does not:

- modify runtime code,
- apply fixes automatically,
- append events to ARTIFACT_INDEX,
- bypass risk or governance engines,
- execute rollback or correction actions.

## System Position

```text
SYSTEM_MAP_2_0
-> VALIDATION_CHECKLIST_LAYER
-> ENGINEERING_BLUEPRINT_MODE
-> CODEBASE_SKELETON
-> EXECUTABLE_BOOTSTRAP_CODEBASE
-> LIVE_SYNCHRONIZATION_LAYER
-> DRIFT_RESPONSE_LAYER
```

## Response Policy

- `CRITICAL` drift -> `BLOCK_EXECUTION`
- `HIGH` event/governance drift -> `ROLLBACK`
- `HIGH` structural/behavioral/lineage drift -> `STAGE_FIX`
- `MEDIUM` structural/event/governance drift -> `STAGE_FIX`
- `MEDIUM` lineage/behavioral drift -> `REVALIDATE`
- no drift -> `NO_ACTION`

`STAGE_FIX`, `ROLLBACK`, and `BLOCK_EXECUTION` require governance approval.
Every staged proposal has `auto_apply=false` and `runtime_mutation=false`.

## Local Check

```powershell
python -B -m unittest tests.test_drift_response_engine
```
