# SCHEMA_CONSISTENCY_GUARD_REPORT.md

## Files created

- `tools/check_schema_consistency.py`
- `tests/test_schema_consistency_guard.py`
- `reports/codex/SCHEMA_CONSISTENCY_GUARD_REPORT.md`

## Files updated

- `tools/run_local_verification.py`
- `tests/test_local_verification_wrapper.py`
- `contracts/compatibility_matrix.v0.1.json`
- `docs/05_CONTRACT_COMPATIBILITY_MATRIX.md`
- `docs/04_VERIFICATION.md`
- `README.md`
- `reports/README.md`
- `reports/codex/LOCAL_SMOKE_WRAPPER_REPORT.md`
- `source_references/GPTMEAi_SELECTED_FILES.md`
- `source_references/SEMASCRIPT_SELECTED_FILES.md`
- `source_references/MANIFEST.md`

## Consistency rules enforced

- SEMASCRIPT action document schema required fields must be listed in the
  compatibility matrix.
- GPTMEAi planner preview schema required fields must be listed in the
  compatibility matrix.
- Execution approval schema required fields must be listed in the compatibility
  matrix.
- Adapter error model schema required fields must be listed in the compatibility
  matrix.
- Matrix scope must remain `dry-run`.
- Unsupported v0.1 boundaries must include:
  - real execution
  - memory mutation
  - storage mutation
  - ledger mutation
  - runtime mutation
  - dependency installation
- Unsupported execution/mutation boundaries must not be marked `supported`.
- `docs/05_CONTRACT_COMPATIBILITY_MATRIX.md` must mention `dry-run` and the
  required unsupported boundaries.

## Tests added

- `tests/test_schema_consistency_guard.py`
  - Checks checker script existence.
  - Checks current project consistency.
  - Checks required schema fields against matrix field names.
  - Checks `dry-run` scope.
  - Checks unsupported v0.1 boundaries.
  - Checks fake matrix missing a required action document field fails.
  - Checks fake matrix marking execution as supported fails.

## Verification commands run

```powershell
python -B -m unittest discover -s tests -p test_schema_consistency_guard.py
python -B tools\check_schema_consistency.py
python -B -m unittest discover -s tests
python -B tools\check_root_cleanliness.py
python -B tools\verify_bridge.py
python -B tools\collect_source_references.py
python -B tools\run_local_verification.py
```

## Verification results

- Targeted schema guard tests RED before implementation:
  - `Ran 8 tests`
  - `FAILED (failures=7)`
  - Failure reason: missing `tools/check_schema_consistency.py`
- Wrapper order test RED before wrapper update:
  - `Ran 6 tests`
  - `FAILED (failures=1)`
  - Failure reason: missing `python -B tools\check_schema_consistency.py` in
    wrapper command list
- First schema guard GREEN attempt found real drift:
  - `planner_preview missing required fields: version`
  - Fixed by adding `planner_preview.version` to the matrix and docs
- Targeted schema guard tests after implementation:
  - `Ran 8 tests`
  - `OK`
- Wrapper order tests after update:
  - `Ran 6 tests`
  - `OK`
- Standalone schema consistency:
  - `SCHEMA_CONSISTENCY=OK`
  - `ROOT=D:\GPTMEAi-SEMASCRIPT`
- Full unittest:
  - `Ran 40 tests`
  - `OK`
- Root cleanliness:
  - `ROOT_CLEANLINESS=OK`
  - `ROOT=D:\GPTMEAi-SEMASCRIPT`
- Dry-run bridge smoke:
  - `LOCAL_VALIDATION=OK`
  - `DRY_RUN=OK`
  - `APPROVAL_GATE=OK`
  - `GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>`
  - `VERIFY_BRIDGE=OK`
- Source reference collection:
  - `MISSING_COUNT=0`
- Local verification wrapper:
  - all five checks returned `RESULT=OK`
  - `LOCAL_VERIFICATION=OK`

## Updated local smoke wrapper report

- `reports/codex/LOCAL_SMOKE_WRAPPER_REPORT.md`

## Safety confirmations

- `D:\Development GPTMEAi` was not modified.
- `D:\SEMASCRIPT\SEMASCRIPT_current_bundle` was not modified.
- No dependencies were installed or updated.
- No execution endpoint was added.
- No live GPTMEAi runtime startup was required.
- No runtime, storage, memory, or logs were intentionally modified.
- v0.1 remains dry-run only.
- No operational report was written to the project root.

## Notes

- GPTMEAi `/health` timeout remains acceptable because `tools/verify_bridge.py`
  exits 0 and local v0.1 verification does not require a live GPTMEAi runtime.
- Full unittest and wrapper execution required escalated shell permission in
  this sandbox because tests create temporary fake roots under
  `D:\GPTMEAi-SEMASCRIPT\tests`, and source reference/report generation writes
  inside the canonical project workspace.
- Temporary test directories left by the initial sandbox-blocked RED run were
  removed after verifying that each path was inside
  `D:\GPTMEAi-SEMASCRIPT\tests` and had a `tmp*` name.

## Next recommended bounded slice

Add a short contract-maintenance note to `docs/02_INTEGRATION_CONTRACT.md`
stating that schema changes must be accompanied by compatibility matrix updates
and a passing `python -B tools\check_schema_consistency.py`.
