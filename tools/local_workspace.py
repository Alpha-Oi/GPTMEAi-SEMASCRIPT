"""Command-line interface for the persistent offline Local Workspace v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from local_workspace import LocalWorkspaceError, LocalWorkspaceService  # noqa: E402


EXPECTED_ERROR_EXIT = 2
INTERNAL_ERROR_EXIT = 3


class JsonArgumentParser(argparse.ArgumentParser):
    """Raise a stable domain error instead of emitting argparse text errors."""

    def error(self, message):
        raise LocalWorkspaceError("INVALID_ARGUMENT", message)


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def _emit(payload, *, stream=sys.stdout) -> None:
    print(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        file=stream,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        prog="local_workspace.py",
        description="Persistent offline Local Workspace v1",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create an empty workspace")
    init_parser.add_argument("workspace")

    add_parser = subparsers.add_parser("add", help="add one artifact")
    add_parser.add_argument("workspace")
    add_parser.add_argument("--id", dest="artifact_id", required=True)
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--content", required=True)

    list_parser = subparsers.add_parser("list", help="list artifacts")
    list_parser.add_argument("workspace")

    search_parser = subparsers.add_parser("search", help="search artifacts locally")
    search_parser.add_argument("workspace")
    search_parser.add_argument("query")

    validate_parser = subparsers.add_parser("validate", help="validate a workspace")
    validate_parser.add_argument("workspace")
    return parser


def run_command(args, service=None):
    service = service or LocalWorkspaceService()
    if args.command == "init":
        document = service.init(args.workspace)
        return {
            "status": "ok",
            "command": "init",
            "path": args.workspace,
            "artifact_count": len(document["artifacts"]),
        }
    if args.command == "add":
        document = service.add(
            args.workspace,
            args.artifact_id,
            args.title,
            args.content,
        )
        return {
            "status": "ok",
            "command": "add",
            "artifact_id": args.artifact_id.strip(),
            "artifact_count": len(document["artifacts"]),
        }
    if args.command == "list":
        artifacts = service.list_artifacts(args.workspace)
        return {
            "status": "ok",
            "command": "list",
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
        }
    if args.command == "search":
        artifacts = service.search(args.workspace, args.query)
        return {
            "status": "ok",
            "command": "search",
            "query": args.query,
            "match_count": len(artifacts),
            "artifacts": artifacts,
        }
    if args.command == "validate":
        document = service.validate(args.workspace)
        return {
            "status": "ok",
            "command": "validate",
            "artifact_count": len(document["artifacts"]),
        }
    raise LocalWorkspaceError("INVALID_ARGUMENT", f"unknown command: {args.command}")


def main(argv=None) -> int:
    _configure_utf8_streams()
    try:
        args = build_parser().parse_args(argv)
        _emit(run_command(args))
        return 0
    except LocalWorkspaceError as exc:
        _emit(
            {
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
            },
            stream=sys.stderr,
        )
        return EXPECTED_ERROR_EXIT
    except Exception:
        _emit(
            {
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": "unexpected internal error",
            },
            stream=sys.stderr,
        )
        return INTERNAL_ERROR_EXIT


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
