# GPTMEAi-SEMASCRIPT Project Contract

This repository is a bridge, not a replacement for GPTMEAi or SEMASCRIPT.

## Source Projects

- `D:\Development GPTMEAi` is read-only input.
- `D:\SEMASCRIPT\SEMASCRIPT_current_bundle` is read-only input.
- Do not modify, merge, vendor, or destructively synchronize either source project.
- Do not copy whole projects into this repository.

## Source Of Truth

- Integration contracts in `contracts/` are the source of truth for bridge behavior.
- Documentation in `docs/` explains decisions and future direction.
- Python modules in `bridge/` and `adapters/` must implement only the approved contract surface.

## v0.1 Runtime Boundary

- v0.1 is dry-run and preview-only.
- No direct runtime mutation is allowed.
- No GPTMEAi memory, storage, ledger, runtime, or execution mutation is allowed.
- No SEMASCRIPT runtime, session, workspace, or lineage mutation is allowed.
- Future execution must pass through an explicit approval gate.
- v0.1 must not expose an execution method or mutation client.

## Protected Zones

Never copy or modify:

- `.env`, secrets, credentials, tokens, keys, certificates
- `.git`
- `.venv`, `venv`, `venv_new`, `env`, `site-packages`
- `node_modules`
- `dist`, `build`, `out`
- logs, runtime data, storage, memory, backups, legacy, tmp, generated artifacts
- databases and user data

## Dependencies

- v0.1 uses the Python standard library only.
- Do not install, update, or repair dependencies without explicit task scope.
- Do not modify lockfiles or package-manager state unless explicitly approved.

## Report / Artifact Placement Rules

- Do not write Codex task reports into the project root.
- Write Codex reports to `reports/codex/`.
- Use descriptive timestamped names when useful.
- Keep root limited to canonical project files.
- Do not place temporary analysis artifacts in `docs/` unless they are stable project documentation.
- Do not delete reports unless explicitly requested.

## Verification

After code or contract changes, run the narrowest meaningful verification first:

```powershell
python -m unittest discover -s tests
python tools/verify_bridge.py
```

If verification cannot run, report the exact command and reason.

---

## Optional GPTMAIOS Sci-Fi Engineering Terminology V4 layer

This project may use:

`docs/knowledge/22_GPTMAIOS_SCI_FI_ENGINEERING_TERMINOLOGY_V4_QUALITY_EXPANSION.md`

as an optional diagnostic terminology layer for complex engineering tasks.

It is additive only. It must not override:
- current user prompt;
- this AGENTS.md / project contract;
- actual project files;
- tests, logs, command outputs;
- Source of Truth;
- Evidence / Inference / Hypothesis discipline;
- DCTP / 10D checklist;
- Definition of Done;
- rollback/change safety.

For usage guardrails, see `docs/knowledge/GPTMAIOS_SCI_FI_V4_USAGE_GUARD_CHECKLIST.md`.

Use V4 only by this formula:

`Term -> engineering meaning -> check -> safe action`

Do not use V4 decoratively.
Use only terms that produce a concrete check, risk note, test, architectural constraint, rollback plan, or next safe action.
