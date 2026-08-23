# LIVE_READONLY_REPORT_TO_SNAPSHOT_ADAPTER_REPORT.md

## Task

Add an optional adapter that converts an already-produced
`reports/codex/GPTMEAI_LIVE_READONLY_STATUS_REPORT.md` markdown report into the
canonical GPTMEAi readonly status snapshot shape.

## Project Root

`D:\GPTMEAi-SEMASCRIPT`

## Files Created

- `bridge/gptmeai_live_report_adapter.py`
- `tests/test_gptmeai_live_report_adapter.py`
- `tests/fixtures/compatibility/gptmeai_live_readonly_report.unavailable.md`
- `tests/fixtures/compatibility/gptmeai_live_readonly_snapshot_from_report.expected.json`
- `reports/codex/LIVE_READONLY_REPORT_TO_SNAPSHOT_ADAPTER_REPORT.md`

## Files Updated

- `docs/02_INTEGRATION_CONTRACT.md`
- `docs/04_VERIFICATION.md`
- `docs/06_HANDOFF_CHECKLIST.md`
- `reports/codex/LOCAL_SMOKE_WRAPPER_REPORT.md` by required local verification
- `source_references/GPTMEAi_SELECTED_FILES.md` by required source reference refresh
- `source_references/SEMASCRIPT_SELECTED_FILES.md` by required source reference refresh
- `source_references/MANIFEST.md` by required source reference refresh

## Adapter Behavior

- Parses saved markdown report text for `/health`, `/planner/status`, and
  `/execution/status` sections.
- Maps unavailable endpoints to `None` before calling
  `bridge.gptmeai_status_snapshot.build_status_snapshot(...)`.
- Preserves available JSON object payloads through the existing snapshot mapper.
- Produces `unavailable`, `degraded`, or `ok` snapshot status according to
  endpoint availability.
- Keeps snapshot metadata `dry_run: true`, `read_only: true`, and
  `live_required: false`.

## Fixtures Added

- Unavailable live-readonly markdown report fixture.
- Expected canonical snapshot fixture for the unavailable report.

## Tests Added

`tests/test_gptmeai_live_report_adapter.py` covers:

- adapter file existence;
- unavailable report conversion;
- mixed degraded conversion;
- all-available OK conversion;
- required schema top-level fields;
- metadata safety flags;
- no live checker/client import or mutation endpoint strings;
- `tools/run_local_verification.py` still not calling the live checker.

## Verification Commands Run

```powershell
python -B -m unittest discover -s tests -p test_gptmeai_live_report_adapter.py
python -B -m unittest discover -s tests -p test_live_readonly_optional_guard.py
python -B tools\check_schema_consistency.py
python -B -m unittest discover -s tests
python -B tools\check_root_cleanliness.py
python -B tools\run_local_verification.py
```

## Verification Results

- RED targeted adapter test before implementation: expected failure because
  `bridge.gptmeai_live_report_adapter` did not exist yet.
- Targeted adapter tests after implementation: `Ran 8 tests`, `OK`.
- Optional live-readonly guard tests: `Ran 4 tests`, `OK`.
- Schema consistency: `SCHEMA_CONSISTENCY=OK`.
- Full unittest first non-escalated run: failed due sandbox write permission when
  existing tests attempted to create temporary fake roots under `tests\tmp*`.
- Full unittest rerun with required filesystem permission: `Ran 69 tests`, `OK`.
- Root cleanliness: `ROOT_CLEANLINESS=OK`.
- Local verification wrapper: `LOCAL_VERIFICATION=OK`.

Temporary `tests\tmp*` directories left by the sandbox-blocked unittest attempt
were removed after verifying that each resolved path was inside
`D:\GPTMEAi-SEMASCRIPT\tests`.

## Safety Confirmations

- Adapter performs no network calls.
- Adapter does not import the live checker.
- Adapter does not import or call a GPTMEAi live read-only client.
- Adapter does not contain mutation/execution endpoint strings checked by tests.
- `tools/run_local_verification.py` does not call
  `check_gptmeai_live_readonly.py`.
- Live checker remains optional and is not required for v0.1 local verification.
- `D:\Development GPTMEAi` was not modified.
- `D:\SEMASCRIPT\SEMASCRIPT_current_bundle` was not modified.
- No dependencies were installed.
- No execution was enabled.
- v0.1 remains dry-run only.
- No reports were written into the project root.

## Risks / Remaining Debt

- The markdown parser is intentionally conservative and recognizes the current
  live-readonly report format plus small formatting variations. A future major
  report format change should update tests and parser together.

## Next Recommended Bounded Slice

Add an optional CLI utility that converts a saved live-readonly report file into
a snapshot JSON artifact under `reports/codex/`, without adding it to required
local verification.
