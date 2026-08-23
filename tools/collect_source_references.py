"""Collect read-only source reference manifests for GPTMEAi and SEMASCRIPT."""

from datetime import datetime, timezone
from pathlib import Path

TARGET_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = TARGET_ROOT / "source_references"

GPTMEAI_SOURCE_ROOT = Path("D:/Development GPTMEAi")
SEMASCRIPT_SOURCE_ROOT = Path("D:/SEMASCRIPT/SEMASCRIPT_current_bundle")

GPTMEAI_REFERENCES = [
    "README.md",
    "AGENTS.md",
    "run_ai_os.py",
    "scripts/api_server.py",
    "ai_os",
    "planning",
    "execution",
    "core",
    "docs/developer",
    "AI_OS_DEVELOPMENT_INVARIANTS.md",
    "AI_OS_LAYER_TECHNICAL_SPEC.md",
]

SEMASCRIPT_REFERENCES = [
    "README.md",
    "AGENTS.md",
    "docs",
    "tooling/semascript_parser.py",
    "tooling/semascript_ast.py",
    "tooling/semascript_validator.py",
    "tooling/exec_runtime.py",
    "tooling/inspector_server.py",
    "tooling/inspector_service.py",
    "tooling/state_model.py",
    "tooling/session_model.py",
    "tooling/project_model.py",
]

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "venv_new",
    "env",
    "node_modules",
    "dist",
    "build",
    "out",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "logs",
    "runtime",
    "storage",
    "memory",
    "backups",
    "backup_python_files",
    "legacy",
    "tmp",
}

SENSITIVE_NAMES = {".env", ".env.local", ".env.production"}
SENSITIVE_SUFFIXES = {".pem", ".pfx", ".key", ".crt", ".cert"}
SENSITIVE_TOKENS = ("secret", "token", "credential", "password")


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_excluded(path):
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts.intersection(EXCLUDED_PARTS):
        return True
    name = path.name.lower()
    if name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    return any(token in name for token in SENSITIVE_TOKENS)


def _selected_children(directory, limit=40):
    children = []
    try:
        iterator = directory.rglob("*")
        for child in iterator:
            if _is_excluded(child):
                continue
            if child.is_file():
                children.append(child)
            if len(children) >= limit:
                break
    except OSError:
        return []
    return children


def _entry(root, relative_path):
    path = root / relative_path
    if not path.exists() or _is_excluded(path):
        return None
    if path.is_dir():
        children = _selected_children(path)
        child_lines = [
            f"  - `{child.relative_to(root).as_posix()}`" for child in children
        ] or ["  - No selected files found."]
        return "\n".join(
            [
                f"- `{relative_path}`",
                "  - Type: directory",
                f"  - Absolute path: `{path}`",
                "  - Selected children:",
                *child_lines,
            ]
        )
    if path.is_file():
        return "\n".join(
            [
                f"- `{relative_path}`",
                "  - Type: file",
                f"  - Absolute path: `{path}`",
                f"  - Size bytes: {path.stat().st_size}",
            ]
        )
    return None


def _write_project_reference(filename, title, root, references):
    found = []
    missing = []
    for relative in references:
        entry = _entry(root, relative)
        if entry is None:
            missing.append(relative)
        else:
            found.append(entry)

    lines = [
        f"# {title}",
        "",
        f"- Generated: `{_utc_now()}`",
        f"- Source root: `{root}`",
        "- Mode: read-only path reference; no source files copied.",
        "",
        "## Selected References",
        "",
        *found,
        "",
        "## Missing / Not Found",
        "",
        *[f"- `{item}`" for item in missing],
        "",
    ]
    (OUTPUT_ROOT / filename).write_text("\n".join(lines), encoding="utf-8")
    return found, missing


def main():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    gpt_found, gpt_missing = _write_project_reference(
        "GPTMEAi_SELECTED_FILES.md",
        "GPTMEAi Selected Files",
        GPTMEAI_SOURCE_ROOT,
        GPTMEAI_REFERENCES,
    )
    sema_found, sema_missing = _write_project_reference(
        "SEMASCRIPT_SELECTED_FILES.md",
        "SEMASCRIPT Selected Files",
        SEMASCRIPT_SOURCE_ROOT,
        SEMASCRIPT_REFERENCES,
    )

    manifest_lines = [
        "# Source Reference Manifest",
        "",
        f"- Generated: `{_utc_now()}`",
        f"- Target root: `{TARGET_ROOT}`",
        f"- GPTMEAi source root: `{GPTMEAI_SOURCE_ROOT}`",
        f"- SEMASCRIPT source root: `{SEMASCRIPT_SOURCE_ROOT}`",
        "- Source mode: read-only reference manifest only.",
        "- Files copied from source projects: none.",
        "",
        "## Excluded Zones",
        "",
        *[f"- `{item}`" for item in sorted(EXCLUDED_PARTS)],
        "- secret-bearing filenames, tokens, keys, certificates, and `.env*` files",
        "",
        "## Counts",
        "",
        f"- GPTMEAi selected reference entries: {len(gpt_found)}",
        f"- SEMASCRIPT selected reference entries: {len(sema_found)}",
        f"- Missing / not found entries: {len(gpt_missing) + len(sema_missing)}",
        "",
        "## Missing / Not Found",
        "",
        "### GPTMEAi",
        "",
        *[f"- `{item}`" for item in gpt_missing],
        "",
        "### SEMASCRIPT",
        "",
        *[f"- `{item}`" for item in sema_missing],
        "",
    ]
    (OUTPUT_ROOT / "MANIFEST.md").write_text("\n".join(manifest_lines), encoding="utf-8")

    print(f"WROTE={OUTPUT_ROOT / 'GPTMEAi_SELECTED_FILES.md'}")
    print(f"WROTE={OUTPUT_ROOT / 'SEMASCRIPT_SELECTED_FILES.md'}")
    print(f"WROTE={OUTPUT_ROOT / 'MANIFEST.md'}")
    print(f"MISSING_COUNT={len(gpt_missing) + len(sema_missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
