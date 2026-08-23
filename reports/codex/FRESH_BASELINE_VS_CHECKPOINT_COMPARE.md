# FRESH_BASELINE_VS_CHECKPOINT_COMPARE.md

## Purpose
Fresh verification baseline compared against Artifact OS checkpoint before Stage 4 design.

## Decision
BASELINE_CONFIRMED_WITH_NOTES

## Project stage
Stage 3 — Bridge stabilized with smoke/check artifacts.

## Inputs
- AGENTS.md
- reports\codex\ARTIFACT_OS_CHECKPOINT_SUMMARY.md
- reports\codex\ARTIFACT_INDEX.json
- tools\run_local_verification.py

## Fresh verification result
`python -B tools\run_local_verification.py` completed successfully.

```text
LOCAL_VERIFICATION_ROOT=D:\GPTMEAi-SEMASCRIPT
RUNNING=python -B tools\check_root_cleanliness.py
RESULT=OK exit_code=0 duration_seconds=0.069
RUNNING=python -B tools\check_schema_consistency.py
RESULT=OK exit_code=0 duration_seconds=0.075
RUNNING=python -B -m unittest discover -s tests
RESULT=OK exit_code=0 duration_seconds=0.563
RUNNING=python -B tools\verify_bridge.py
RESULT=OK exit_code=0 duration_seconds=1.3
RUNNING=python -B tools\collect_source_references.py
RESULT=OK exit_code=0 duration_seconds=0.242
LOCAL_VERIFICATION_REPORT=D:\GPTMEAi-SEMASCRIPT\reports\codex\LOCAL_SMOKE_WRAPPER_REPORT.md
LOCAL_VERIFICATION=OK
```

Fresh `LOCAL_SMOKE_WRAPPER_REPORT.md` contains:
- `ROOT_CLEANLINESS=OK`
- `SCHEMA_CONSISTENCY=OK`
- `Ran 107 tests in 0.231s` and `OK`
- `LOCAL_VALIDATION=OK`
- `DRY_RUN=OK`
- `APPROVAL_GATE=OK`
- `GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>`
- `VERIFY_BRIDGE=OK`
- `MISSING_COUNT=0`

## Checkpoint comparison table
| Category | Checkpoint | Fresh baseline | Result | Notes |
|---|---|---|---|---|
| Registry identity | `D:\GPTMEAi-SEMASCRIPT\reports\codex\ARTIFACT_INDEX.json`, version `0.9` | same path, version `0.9` | MATCH | Root `ARTIFACT_INDEX.json` remains absent; checkpoint uses `reports/codex`. |
| Artifact count | `14` | `14` | MATCH | Confirmed from `ARTIFACT_INDEX.json`. |
| Event count | `35` | `35` | MATCH | Confirmed from `ARTIFACT_INDEX.json`. |
| Constraints | `no_execution=True`, `read_only=True`, `no_external_deps=True` | same constraints | MATCH | JSON values stable. |
| Last green verification evidence | checkpoint preserved `4 tests OK`, `107 tests OK`, `7 tests OK`, `VERIFY_BRIDGE=OK`, `ROOT_CLEANLINESS=OK` | fresh wrapper confirms `107 tests OK`, `VERIFY_BRIDGE=OK`, `ROOT_CLEANLINESS=OK`, `SCHEMA_CONSISTENCY=OK`, `MISSING_COUNT=0` | MATCH_WITH_NOTES | Wrapper does not separately run nested bootstrap `7 tests`; parent 107-test suite is fresh. |
| Root cleanliness | `ROOT_CLEANLINESS=OK` | `ROOT_CLEANLINESS=OK` | MATCH | Final root cleanliness also passed after removing transient `.pyc`. |
| Schema consistency | expected local verification guard | `SCHEMA_CONSISTENCY=OK` | MATCH | Fresh wrapper confirms. |
| Bridge verification | `VERIFY_BRIDGE=OK`; optional GPTMEAi health unavailable non-fatal | `VERIFY_BRIDGE=OK`; `GPTMEAI_HEALTH=UNAVAILABLE` timeout non-fatal | MATCH_WITH_NOTES | No runtime was started; optional live health remains unavailable. |
| Unit test count/result | checkpoint strongest baseline included parent `107 tests OK` | fresh wrapper ran `107 tests` and `OK` | MATCH | Exact parent suite count remains 107. |
| Live runtime boundary | dry-run/preview-only; no live GPTMEAi execution; no SEMASCRIPT runtime/session mutation | wrapper did not start live runtime; `verify_bridge.py` only attempted optional GPTMEAi health and tolerated timeout | MATCH_WITH_NOTES | Optional `/health` availability remains non-gating. |
| Source project boundary | source projects read-only; source refs missing count 0 | source projects not modified; `collect_source_references.py` refreshed local `source_references\*` and `MISSING_COUNT=0` | MATCH_WITH_NOTES | `source_references\*` hashes changed as normal wrapper output. |
| Stage 3 readiness before Stage 4 design | Stage 3 checkpoint says run fresh local verification before Stage 4 design | fresh local verification passed | MATCH | Stage 4 design can start; Stage 4 implementation is not authorized by this comparison. |

## Hash stability
| File / group | Before | After | Stable |
|---|---|---|---|
| `AGENTS.md` | `FF2FB0CAC97B9F10AF8FA38877940D523ED190469829FF4FA8CDDBB3F25EB605` | `FF2FB0CAC97B9F10AF8FA38877940D523ED190469829FF4FA8CDDBB3F25EB605` | `True` |
| `reports\codex\ARTIFACT_INDEX.json` | `8CC43F7CEC83B0E82009AB0C61EC7AA36E1AECDA0AA4364660C53F8709CFF5C5` | `8CC43F7CEC83B0E82009AB0C61EC7AA36E1AECDA0AA4364660C53F8709CFF5C5` | `True` |
| `reports\codex\ARTIFACT_OS_CHECKPOINT_SUMMARY.md` | `349186E6AAA30A7166AE7DDC83CB41FDD75625C054A380316FE1C36839EAA5AC` | `349186E6AAA30A7166AE7DDC83CB41FDD75625C054A380316FE1C36839EAA5AC` | `True` |
| `contracts\adapter_error_model.schema.json` | `553B89A816A1BB18AB4006BD4BEF51613CB0E340AB47DEFEACF32686948F4B1E` | `553B89A816A1BB18AB4006BD4BEF51613CB0E340AB47DEFEACF32686948F4B1E` | `True` |
| `contracts\compatibility_matrix.v0.1.json` | `B171DA802D84D1DE265E07BFE76A1B9F8908EEB4B1B1EBBE08B170253242CB85` | `B171DA802D84D1DE265E07BFE76A1B9F8908EEB4B1B1EBBE08B170253242CB85` | `True` |
| `contracts\drift_response_event.schema.json` | `87623D92D56E33087865DF2388F8F11361885E718D8FB05E9B5E9135429CB061` | `87623D92D56E33087865DF2388F8F11361885E718D8FB05E9B5E9135429CB061` | `True` |
| `contracts\execution_approval.schema.json` | `CCFFC7CC8FACBE374B38288215DCBCD7821AE53DC59B600EA5461D7FEDFCD0C2` | `CCFFC7CC8FACBE374B38288215DCBCD7821AE53DC59B600EA5461D7FEDFCD0C2` | `True` |
| `contracts\execution_enforced_event.schema.json` | `9FEA5DB00AE5C93AF358F337A6BB27A15D22A9C1422F9FFA5797BFA2AB74284A` | `9FEA5DB00AE5C93AF358F337A6BB27A15D22A9C1422F9FFA5797BFA2AB74284A` | `True` |
| `contracts\gptmeai_planner_preview.schema.json` | `AE344B2723BB579DE2C76B81DB57F180F5EC2E810F505D47AC641AA1907257E7` | `AE344B2723BB579DE2C76B81DB57F180F5EC2E810F505D47AC641AA1907257E7` | `True` |
| `contracts\gptmeai_readonly_status_snapshot.schema.json` | `3A53659A74383292759451D7B2BF210B4E4CDA74C8BC5F4D6EFF38750A550C79` | `3A53659A74383292759451D7B2BF210B4E4CDA74C8BC5F4D6EFF38750A550C79` | `True` |
| `contracts\live_sync_drift_event.schema.json` | `8F6290D23612A25C97935A7B5AE2A79580597428C1D7598D462B2E8414CEE229` | `8F6290D23612A25C97935A7B5AE2A79580597428C1D7598D462B2E8414CEE229` | `True` |
| `contracts\semascript_action_document.schema.json` | `E3441633D04341988014D01B3C077B55CE944BA95B78CF515F60776AC741A79E` | `E3441633D04341988014D01B3C077B55CE944BA95B78CF515F60776AC741A79E` | `True` |

Additional observed wrapper side effect:

| File / group | Before | After | Stable |
|---|---|---|---|
| `source_references\GPTMEAi_SELECTED_FILES.md` | `6E352A61F5E33E003F427078549F493A729F885A7CD1E07D8FAAE61054E2BD7B` | `03A8F95E1C0C80890E56363C9EE83D29B91B5C6542188258D489F82E6272AC6F` | `False` |
| `source_references\MANIFEST.md` | `687B52EE844666E4094D576DAEB290A441B9B2F9AF70051A1D6F703E44D8E571` | `D84D1DF6E840287F17336A16D890296E3D8FCCFE05CCC975F22DBD0CC68B6901` | `False` |
| `source_references\SEMASCRIPT_SELECTED_FILES.md` | `87660E9BC047E91BFEA09B78AD0F2B24FAD29BFF8E63EFFBAC29D0E8A478C88D` | `88CAB8DEFDB4A8B2E22EBCB09DBDD08F9B018891D3098CB2547439D1062516DC` | `False` |

## Confirmed facts
- `python -B -m py_compile tools\run_local_verification.py` succeeded.
- `python -B tools\run_local_verification.py` returned `LOCAL_VERIFICATION=OK`.
- Fresh wrapper report was written to `reports\codex\LOCAL_SMOKE_WRAPPER_REPORT.md`.
- `reports\codex\ARTIFACT_INDEX.json` remains version `0.9` with artifact count `14` and event count `35`.
- `AGENTS.md`, `ARTIFACT_INDEX.json`, `ARTIFACT_OS_CHECKPOINT_SUMMARY.md`, and all contract files stayed hash-stable.
- Fresh wrapper result confirms `ROOT_CLEANLINESS=OK`, `SCHEMA_CONSISTENCY=OK`, `107 tests OK`, `VERIFY_BRIDGE=OK`, and `MISSING_COUNT=0`.
- `GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>` remains non-fatal in `verify_bridge.py`.
- `tools\collect_source_references.py` refreshed local `source_references\*` as part of the existing wrapper.
- Final cleanup removed the `.pyc` file created by `py_compile`; final root cleanliness remained OK.

## Inferences
- Current project state remains consistent with the Stage 3 Artifact OS checkpoint.
- No registry drift was detected.
- No contract drift was detected.
- No AGENTS.md drift was detected.
- Stage 4 design can start because the fresh local verification baseline matches the checkpoint on required safety and verification gates.
- Stage 4 implementation should not start from this task; only design is justified by this comparison.

## Drift / mismatches
No blocking drift detected.

Notes:
- `source_references\*` changed because `tools\run_local_verification.py` runs `tools\collect_source_references.py`; this is normal wrapper behavior and ended with `MISSING_COUNT=0`.
- The fresh wrapper does not separately run nested bootstrap tests, so checkpoint marker `7 tests OK` remains preserved historical evidence rather than fresh wrapper evidence.
- Optional GPTMEAi `/health` remains unavailable by timeout, but `VERIFY_BRIDGE=OK` treats this as non-fatal for v0.1.

## Unknowns
- Live GPTMEAi service health remains unknown/unavailable; no live runtime was started.
- SEMASCRIPT live runtime/session behavior was not checked and no live runtime was started.
- Source project filesystem hashes were not computed; source projects were not targeted for writes.
- Stage 4 functional integration design has not yet been written.

## Risks before Stage 4
- Do not treat this bridge as a merged runtime.
- Preserve dry-run/preview-only and approval-gated boundaries until a design-only Stage 4 plan explicitly defines safe transition rules.
- Keep `reports/codex/ARTIFACT_INDEX.json` immutable unless a future explicit registry task authorizes a bounded update.
- Avoid relying on optional live GPTMEAi availability as a gate for v0.1/v0.2 readiness.
- Distinguish local governance/bootstrap skeleton behavior from actual GPTMEAi and SEMASCRIPT runtime behavior.
- Account for `run_local_verification.py` refreshing `source_references\*` when planning future hash or immutability checks.

## Recommended next step
Create a read-only Stage 4 functional integration design brief that defines the first safe functional integration slice, required source evidence, mutation boundaries, approval gates, rollback plan, and verification gates without implementing runtime execution.
