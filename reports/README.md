# Reports

The project root must stay clean and limited to canonical project files.

Codex operational reports go to `reports/codex/`. Root-level reports are not
allowed unless explicitly requested for a specific task.

Stable project documentation belongs in `docs/`. Source reference manifests
belong in `source_references/`.

Temporary review artifacts, task handoffs, verification notes, and Codex cleanup
or migration reports belong in `reports/codex/`.

Handoff reports belong under `reports/codex/`.

Root cleanliness is enforced by `tools/check_root_cleanliness.py`. The checker
fails when operational reports or protected folders are left in the project
root.

The local smoke wrapper `tools/run_local_verification.py` writes its detailed
report to `reports/codex/LOCAL_SMOKE_WRAPPER_REPORT.md`, including schema
consistency results.
