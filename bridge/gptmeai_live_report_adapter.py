"""Convert saved GPTMEAi live read-only reports into status snapshots."""

import json
from pathlib import Path
import re

from bridge.gptmeai_status_snapshot import build_status_snapshot


REPORT_FILENAME = "GPTMEAI_LIVE_READONLY_STATUS_REPORT.md"
ENDPOINT_TO_SECTION = {
    "/health": "health",
    "/planner/status": "planner",
    "/execution/status": "execution",
}
ENDPOINT_HEADING = re.compile(r"^###\s+`(?P<endpoint>[^`]+)`\s*$", re.MULTILINE)
JSON_BLOCK = re.compile(r"```json\s*(?P<body>.*?)\s*```", re.IGNORECASE | re.DOTALL)


def default_report_path() -> Path:
    """Return the default saved live read-only report path."""
    return Path(__file__).resolve().parents[1] / "reports" / "codex" / REPORT_FILENAME


def load_live_readonly_report(path) -> str:
    """Load an already-produced live read-only markdown report."""
    return Path(path).read_text(encoding="utf-8")


def parse_live_readonly_report_text(report_text: str) -> dict:
    """Parse recognized endpoint summaries from a saved markdown report."""
    sections = {
        "health": None,
        "planner": None,
        "execution": None,
    }
    endpoints = {}

    for endpoint, section_text in _endpoint_sections(report_text):
        if endpoint not in ENDPOINT_TO_SECTION:
            continue
        available = _parse_bool(_bullet_value(section_text, "Available"))
        payload = _json_payload(section_text)
        top_level_keys = _top_level_keys(section_text, payload)
        section_name = ENDPOINT_TO_SECTION[endpoint]

        endpoints[endpoint] = {
            "available": bool(available),
            "top_level_keys": top_level_keys,
            "payload": payload if isinstance(payload, dict) else {},
        }
        if available and isinstance(payload, dict):
            sections[section_name] = payload

    return {
        "endpoints": endpoints,
        "sections": sections,
    }


def snapshot_from_live_readonly_report_text(report_text: str, captured_at: str | None = None) -> dict:
    """Convert saved report text into the canonical read-only snapshot."""
    parsed = parse_live_readonly_report_text(report_text)
    sections = parsed["sections"]
    return build_status_snapshot(
        health=sections["health"],
        planner=sections["planner"],
        execution=sections["execution"],
        captured_at=captured_at,
    )


def snapshot_from_live_readonly_report_file(path=None, captured_at: str | None = None) -> dict:
    """Load a saved report file and convert it into the canonical snapshot."""
    report_path = default_report_path() if path is None else Path(path)
    return snapshot_from_live_readonly_report_text(
        load_live_readonly_report(report_path),
        captured_at=captured_at,
    )


def _endpoint_sections(report_text: str):
    matches = list(ENDPOINT_HEADING.finditer(report_text))
    for index, match in enumerate(matches):
        endpoint = match.group("endpoint").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(report_text)
        yield endpoint, report_text[start:end]


def _bullet_value(section_text: str, label: str) -> str:
    pattern = re.compile(rf"^- {re.escape(label)}:\s*(?P<value>.*?)\s*$", re.MULTILINE)
    match = pattern.search(section_text)
    if not match:
        return ""
    return match.group("value").strip().strip("`").strip()


def _parse_bool(raw_value: str) -> bool:
    return raw_value.strip().lower() in {"true", "1", "yes"}


def _json_payload(section_text: str):
    match = JSON_BLOCK.search(section_text)
    if not match:
        return {}
    try:
        payload = json.loads(match.group("body"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _top_level_keys(section_text: str, payload: dict) -> list[str]:
    raw_keys = _bullet_value(section_text, "Top-level keys")
    if raw_keys:
        return [key.strip() for key in raw_keys.split(",") if key.strip()]
    if isinstance(payload, dict):
        return sorted(str(key) for key in payload.keys())
    return []
