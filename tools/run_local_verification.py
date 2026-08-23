"""Run the local GPTMEAi-SEMASCRIPT v0.1 dry-run verification suite."""

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time


CHECK_COMMANDS = (
    ("python", "-B", "tools\\check_root_cleanliness.py"),
    ("python", "-B", "tools\\check_schema_consistency.py"),
    ("python", "-B", "-m", "unittest", "discover", "-s", "tests"),
    ("python", "-B", "tools\\verify_bridge.py"),
    ("python", "-B", "tools\\collect_source_references.py"),
)

REPORT_FILENAME = "LOCAL_SMOKE_WRAPPER_REPORT.md"


def project_root():
    return Path(__file__).resolve().parents[1]


def report_path(root):
    return Path(root) / "reports" / "codex" / REPORT_FILENAME


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _format_command(command):
    return " ".join(command)


def run_check(command, root):
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "command": _format_command(command),
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "duration_seconds": round(time.perf_counter() - started, 3),
        }
    except OSError as exc:
        return {
            "command": _format_command(command),
            "exit_code": 127,
            "stdout": "",
            "stderr": str(exc),
            "duration_seconds": round(time.perf_counter() - started, 3),
        }


def _code_block(text):
    if not text:
        return "```text\n\n```"
    return f"```text\n{text.rstrip()}\n```"


def write_report(root, results):
    path = report_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)

    all_passed = all(result["exit_code"] == 0 for result in results)
    lines = [
        "# LOCAL_SMOKE_WRAPPER_REPORT.md",
        "",
        f"- Generated: `{_utc_now()}`",
        f"- Project root: `{root}`",
        f"- Status: `{'OK' if all_passed else 'FAIL'}`",
        f"- Report path: `{path}`",
        "",
        "## Commands",
        "",
    ]

    for index, result in enumerate(results, start=1):
        lines.extend(
            [
                f"### {index}. `{result['command']}`",
                "",
                f"- Exit code: `{result['exit_code']}`",
                f"- Duration seconds: `{result['duration_seconds']}`",
                "",
                "#### stdout",
                "",
                _code_block(result["stdout"]),
                "",
                "#### stderr",
                "",
                _code_block(result["stderr"]),
                "",
            ]
        )

    lines.extend(
        [
            "## Safety",
            "",
            "- No dependencies were installed by this wrapper.",
            "- No live runtime startup is required by this wrapper.",
            "- Reports are written under `reports/codex/`, not the project root.",
            "- Source projects are referenced only by existing read-only source reference tooling.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main(argv=None):
    _ = argv
    root = project_root()
    results = []

    print(f"LOCAL_VERIFICATION_ROOT={root}")
    for command in CHECK_COMMANDS:
        print(f"RUNNING={_format_command(command)}")
        result = run_check(command, root)
        results.append(result)
        print(
            "RESULT="
            f"{'OK' if result['exit_code'] == 0 else 'FAIL'} "
            f"exit_code={result['exit_code']} "
            f"duration_seconds={result['duration_seconds']}"
        )

    path = write_report(root, results)
    all_passed = all(result["exit_code"] == 0 for result in results)
    print(f"LOCAL_VERIFICATION_REPORT={path}")
    print(f"LOCAL_VERIFICATION={'OK' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
