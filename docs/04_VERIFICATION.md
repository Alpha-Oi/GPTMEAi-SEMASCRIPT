# Verification

Run local tests:

```powershell
python -m unittest discover -s tests
```

Recommended local verification wrapper:

```powershell
python -B tools\run_local_verification.py
```

This wrapper runs the root-cleanliness guard, schema consistency guard, full
unittest suite, dry-run bridge smoke, and source reference refresh in the
expected local order.
Compatibility matrix tests are included in the full unittest suite run by this
wrapper.

Run only the read-only compatibility fixture tests:

```powershell
python -m unittest discover -s tests -p test_compatibility_fixtures.py
```

Check project-root cleanliness:

```powershell
python -B tools\check_root_cleanliness.py
```

Check schema and compatibility matrix consistency:

```powershell
python -B tools\check_schema_consistency.py
```

Schema, matrix, or contract documentation changes require:

```powershell
python -B tools\check_schema_consistency.py
python -B tools\run_local_verification.py
```

Run the dry-run bridge smoke:

```powershell
python tools/verify_bridge.py
```

Collect read-only source references:

```powershell
python tools/collect_source_references.py
```

## Optional Live Read-Only GPTMEAi Check

If GPTMEAi is already running, use:

```powershell
python -B tools\check_gptmeai_live_readonly.py
```

This checks only `/health`, `/planner/status`, and `/execution/status`.
It is optional for v0.1 and must not enable execution or mutation.

If a live-readonly report already exists under `reports/codex/`, the optional
report adapter can convert that saved markdown report into the canonical
readonly status snapshot without performing network calls. This adapter is not
part of required v0.1 local verification.

To write a machine-readable snapshot artifact from an existing report, use:

```powershell
python -B tools\write_gptmeai_readonly_snapshot_from_report.py
```

This writes to `reports/codex/GPTMEAI_READONLY_STATUS_SNAPSHOT_FROM_LIVE_REPORT.json`
by default. It consumes only the saved report file and remains outside the
required local verification wrapper.

Expected local verification:

- valid SEMASCRIPT action document passes manual validation;
- invalid fixture fails validation;
- planner preview has `dry_run: true`;
- planner preview requires approval;
- GPTMEAi client has no `execute` method in v0.1;
- SEMASCRIPT AST compatibility fixture normalizes into a valid action document;
- GPTMEAi health, planner status, and execution status fixtures are parsed as
  static read-only sample payloads;
- GPTMEAi readonly status snapshot fixtures and mapper stay read-only and do
  not require live GPTMEAi availability;
- root-level operational reports and protected folders are blocked by
  `tools/check_root_cleanliness.py`;
- JSON schemas, the compatibility matrix, and matrix documentation remain
  aligned through `tools/check_schema_consistency.py`;
- contract compatibility matrix documentation, JSON, loader, and unsupported
  v0.1 boundaries are covered by `tests/test_contract_compatibility_matrix.py`;
- GPTMEAi `/health` may be unavailable and should not fail the local bridge
  smoke.

Verification must not install dependencies, mutate source projects, start live
runtimes, or call mutation endpoints. Compatibility fixture tests are static
and do not require a GPTMEAi runtime to be running.

Operational reports from verification or Codex tasks should be saved under
`reports/codex/`, not the project root.

Before handoff, follow `docs/06_HANDOFF_CHECKLIST.md`.
