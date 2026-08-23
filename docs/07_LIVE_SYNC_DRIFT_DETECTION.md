# Live Synchronization & Drift Detection

`live_sync/` is a deterministic, read-only monitoring layer between ARTIFACT OS
and the executable bootstrap runtime at `gptmeai-semascript/`.

It detects and reports:

- structural drift,
- behavioral drift,
- event drift,
- governance drift,
- lineage drift.

It does not:

- execute runtime logic,
- modify runtime files,
- append events to ARTIFACT_INDEX,
- fix drift automatically,
- bypass governance or risk checks.

## Integration Position

```text
SYSTEM_MAP_2_0
-> VALIDATION_CHECKLIST_LAYER
-> ENGINEERING_BLUEPRINT_MODE
-> CODEBASE_SKELETON
-> EXECUTABLE_BOOTSTRAP_CODEBASE
-> LIVE_SYNCHRONIZATION_DRIFT_DETECTION_LAYER
```

## Local Check

```powershell
python -B -m unittest tests.test_live_sync_drift_detection
```

The sync engine emits event objects in memory only. A future governed slice may
register those events in ARTIFACT_INDEX after explicit approval.
