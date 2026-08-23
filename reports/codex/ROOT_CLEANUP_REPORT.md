# ROOT_CLEANUP_REPORT.md

## Task

Clean up root-level operational reports and establish a root-cleanliness rule.

## Files moved

Moved from project root to `reports/codex/`:

- `CANONICAL_WORKSPACE_CONFIRMATION.md` -> `reports/codex/CANONICAL_WORKSPACE_CONFIRMATION.md`
- `COMPATIBILITY_FIXTURES_REPORT.md` -> `reports/codex/COMPATIBILITY_FIXTURES_REPORT.md`
- `MIGRATION_REPORT.md` -> `reports/codex/MIGRATION_REPORT.md`

No filename conflicts were found, so no timestamp prefixes were needed.

## Files left in root

Root now contains canonical project entries only:

- `AGENTS.md`
- `README.md`
- `.env.example`
- `adapters/`
- `bridge/`
- `contracts/`
- `docs/`
- `examples/`
- `reports/`
- `source_references/`
- `tests/`
- `tools/`

## AGENTS.md update summary

Added `## Report / Artifact Placement Rules` with these rules:

- do not write Codex task reports into the project root;
- write Codex reports to `reports/codex/`;
- use descriptive timestamped names when useful;
- keep root limited to canonical project files;
- do not place temporary analysis artifacts in `docs/` unless they are stable project documentation;
- do not delete reports unless explicitly requested.

## reports/README.md status

Created `reports/README.md`.

It states that:

- root must stay clean;
- Codex operational reports go to `reports/codex/`;
- root-level reports are not allowed unless explicitly requested;
- stable project documentation belongs in `docs/`;
- source reference manifests belong in `source_references/`;
- temporary review artifacts belong in `reports/codex/`.

## docs/04_VERIFICATION.md update summary

Added a note that operational reports from verification or Codex tasks should be saved under `reports/codex/`, not the project root.

## Verification commands run

```powershell
python -B -m unittest discover -s tests
python -B tools\verify_bridge.py
python -B tools\collect_source_references.py
```

## Verification results

Unit tests:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 0.004s

OK
```

Dry-run bridge smoke:

```text
LOCAL_VALIDATION=OK
DRY_RUN=OK
APPROVAL_GATE=OK
GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>
VERIFY_BRIDGE=OK
```

Source references:

```text
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\GPTMEAi_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\SEMASCRIPT_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\MANIFEST.md
MISSING_COUNT=0
```

## Safety confirmations

- GPTMEAi source project `D:\Development GPTMEAi` was not modified.
- SEMASCRIPT source project `D:\SEMASCRIPT\SEMASCRIPT_current_bundle` was not modified.
- No dependencies were installed or updated.
- No execution was enabled.
- No source files were deleted.
- Reports were moved, not deleted.
- v0.1 remains dry-run only.

## Next recommended bounded slice

Add a lightweight root-cleanliness test or verification tool check that fails if root-level `*_REPORT.md`, `*_CONFIRMATION.md`, or `CHATGPT_REVIEW_REPORT.md` files appear outside `reports/codex/`.
