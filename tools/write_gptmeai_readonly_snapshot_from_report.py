"""Write a GPTMEAi read-only status snapshot from a saved markdown report."""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.gptmeai_live_report_adapter import (  # noqa: E402
    default_report_path,
    snapshot_from_live_readonly_report_file,
)


OUTPUT_FILENAME = "GPTMEAI_READONLY_STATUS_SNAPSHOT_FROM_LIVE_REPORT.json"


def project_root() -> Path:
    """Return the canonical project root for this tool."""
    return ROOT


def default_output_path(root=None) -> Path:
    """Return the default snapshot artifact path under reports/codex."""
    base = project_root() if root is None else Path(root)
    return base / "reports" / "codex" / OUTPUT_FILENAME


def write_snapshot_from_report(report_path=None, output_path=None, captured_at=None) -> Path:
    """Convert a saved markdown report into a canonical snapshot JSON artifact."""
    source_report = default_report_path() if report_path is None else Path(report_path)
    destination = default_output_path() if output_path is None else Path(output_path)
    snapshot = snapshot_from_live_readonly_report_file(
        path=source_report,
        captured_at=captured_at,
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        default=None,
        help="Saved live-readonly markdown report path. Defaults to reports/codex.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Snapshot JSON output path. Defaults to reports/codex.",
    )
    parser.add_argument(
        "--captured-at",
        default=None,
        help="Optional captured_at timestamp to place in the snapshot.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    output = write_snapshot_from_report(
        report_path=args.report,
        output_path=args.output,
        captured_at=args.captured_at,
    )

    snapshot = json.loads(output.read_text(encoding="utf-8"))
    print(f"SNAPSHOT_OUTPUT={output}")
    print(f"SNAPSHOT_STATUS={snapshot['status']}")
    print("SNAPSHOT_SOURCE=live-readonly-report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
