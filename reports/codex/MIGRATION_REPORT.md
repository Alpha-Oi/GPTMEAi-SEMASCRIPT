# MIGRATION_REPORT.md

## Source workspace path

`C:\Users\Crown-Aliy\Documents\New project 2`

## Target path

`D:\GPTMEAi-SEMASCRIPT`

## Migration mode

Copy-first migration. The current workspace copy was not deleted or moved.

## Copied files/folders

Copied from CURRENT_WORKSPACE to TARGET_ROOT:

- `AGENTS.md`
- `README.md`
- `.env.example`
- `docs/`
- `contracts/`
- `bridge/`
- `adapters/`
- `examples/`
- `tests/`
- `tools/`
- `source_references/`

Created after copy:

- `MIGRATION_REPORT.md`

## Skipped files/folders

Skipped by rule and not copied:

- `.git/`
- `__pycache__/`
- `.env`
- `venv/`
- `venv_new/`
- `node_modules/`
- `runtime/`
- `storage/`
- `logs/`
- `memory/chats/`
- `memory/embeddings/`
- `backups/`
- `smart_trash/`
- `legacy/`
- `dist/`
- `build/`

No protected/runtime folders were present in the copied allowlist during final scan.

## Conflicts found

None.

`D:\GPTMEAi-SEMASCRIPT` existed before copy and was empty (`TARGET_ITEM_COUNT=0`), so no unrelated target files were overwritten.

## Root reference updates performed

Searched only inside TARGET_ROOT.

Updated one generated source reference line from:

`C:\Users\Crown-Aliy\Documents\New project 2`

To:

`D:\GPTMEAi-SEMASCRIPT`

Final post-update scan found no remaining occurrences of:

- `C:\Users\Crown-Aliy\Documents\New project 2`
- `New project 2`

Source project paths were intentionally preserved:

- `D:\Development GPTMEAi`
- `D:\SEMASCRIPT\SEMASCRIPT_current_bundle`

After `collect_source_references.py`, `source_references/MANIFEST.md` was regenerated with target root `D:\GPTMEAi-SEMASCRIPT`.

## Verification commands run

```powershell
Set-Location "D:\GPTMEAi-SEMASCRIPT"
python -B -m unittest discover -s tests
python -B tools\verify_bridge.py
python -B tools\collect_source_references.py
```

Additional safety checks:

```powershell
Get-ChildItem -Force -Recurse -LiteralPath 'D:\GPTMEAi-SEMASCRIPT' | Where-Object { $_.Name -in @('.git','__pycache__','.env','venv','venv_new','node_modules','runtime','storage','logs','memory','backups','smart_trash','legacy','dist','build') }
Get-ChildItem -LiteralPath 'D:\GPTMEAi-SEMASCRIPT' -Recurse -File -Force | Select-String -SimpleMatch 'C:\Users\Crown-Aliy\Documents\New project 2','New project 2'
```

## Verification results

### Unit tests

Command:

```powershell
Set-Location 'D:\GPTMEAi-SEMASCRIPT'; python -B -m unittest discover -s tests
```

Result:

```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.002s

OK
```

### Dry-run bridge smoke

Command:

```powershell
Set-Location 'D:\GPTMEAi-SEMASCRIPT'; python -B tools\verify_bridge.py
```

Result:

```text
LOCAL_VALIDATION=OK
DRY_RUN=OK
APPROVAL_GATE=OK
GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>
VERIFY_BRIDGE=OK
```

GPTMEAi `/health` was unavailable by timeout and was correctly treated as optional/unavailable by the dry-run verifier.

### Source reference collection

Command:

```powershell
Set-Location 'D:\GPTMEAi-SEMASCRIPT'; python -B tools\collect_source_references.py
```

Result:

```text
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\GPTMEAi_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\SEMASCRIPT_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\MANIFEST.md
MISSING_COUNT=0
```

## Safety confirmations

- `.git` was not copied.
- GPTMEAi source project `D:\Development GPTMEAi` was not modified.
- SEMASCRIPT source project `D:\SEMASCRIPT\SEMASCRIPT_current_bundle` was not modified.
- No secrets were copied.
- No `.env` file was copied.
- No runtime/protected folders were copied.
- No dependency install/update was run.
- No files were deleted from CURRENT_WORKSPACE.
- No unrelated files existed in TARGET_ROOT before copy.

## Next recommended safe step

Open `D:\GPTMEAi-SEMASCRIPT` as the canonical standalone workspace and run the same verification commands once from that workspace before starting the next bounded development slice.
