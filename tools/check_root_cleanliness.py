"""Check that operational reports and protected folders stay out of project root."""

from pathlib import Path
import sys

ROOT_REPORT_PATTERNS = (
    "*_REPORT.md",
    "*_CONFIRMATION.md",
    "CHATGPT_REVIEW_REPORT.md",
)

FORBIDDEN_ROOT_ENTRIES = {
    ".env",
    ".git",
    ".git_backup",
    ".git-old",
    ".git.tmp",
    "venv",
    "venv_new",
    "node_modules",
    "runtime",
    "storage",
    "logs",
    "memory",
    "backups",
    "smart_trash",
    "legacy",
    "dist",
    "build",
    "__pycache__",
}

ALLOWED_ROOT_ENTRIES = {".git"}


def _root_report_files(root):
    matches = []
    for pattern in ROOT_REPORT_PATTERNS:
        matches.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted({path.name for path in matches})


def check_root_cleanliness(root=None):
    """Return structured root-cleanliness result for a non-recursive root scan."""
    project_root = Path.cwd() if root is None else Path(root)
    violations = []

    if not project_root.exists() or not project_root.is_dir():
        return {
            "ok": False,
            "root": str(project_root),
            "violations": [f"root is not a directory: {project_root}"],
        }

    for name in _root_report_files(project_root):
        violations.append(f"root report file: {name}")

    for entry_name in sorted(FORBIDDEN_ROOT_ENTRIES):
        if (project_root / entry_name).exists() and entry_name not in ALLOWED_ROOT_ENTRIES:
            violations.append(f"forbidden root entry: {entry_name}")

    return {
        "ok": not violations,
        "root": str(project_root),
        "violations": violations,
    }


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
    result = check_root_cleanliness(root)

    if result["ok"]:
        print("ROOT_CLEANLINESS=OK")
        print(f"ROOT={result['root']}")
        return 0

    print("ROOT_CLEANLINESS=FAIL")
    print(f"ROOT={result['root']}")
    for violation in result["violations"]:
        print(f"- {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
