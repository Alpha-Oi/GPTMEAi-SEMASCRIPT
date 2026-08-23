"""Build read-only GPTMEAi status snapshots from static status payloads."""

from copy import deepcopy
from datetime import datetime, timezone


SNAPSHOT_VERSION = "0.2-prep"
SNAPSHOT_SOURCE = "gptmeai"


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def summarize_payload(payload) -> dict:
    """Return a read-only section summary without mutating the input payload."""
    if payload is None:
        return {
            "available": False,
            "top_level_keys": [],
            "payload": {},
        }
    if not isinstance(payload, dict):
        return {
            "available": False,
            "top_level_keys": [],
            "payload": {},
            "uninterpretable": True,
        }
    return {
        "available": True,
        "top_level_keys": sorted(str(key) for key in payload.keys()),
        "payload": deepcopy(payload),
    }


def derive_snapshot_status(health, planner, execution) -> str:
    """Derive snapshot status from section availability."""
    sections = (health, planner, execution)
    if any(section is not None and not isinstance(section, dict) for section in sections):
        return "unknown"

    available_count = sum(section is not None for section in sections)
    if available_count == 3:
        return "ok"
    if available_count == 0:
        return "unavailable"
    return "degraded"


def build_status_snapshot(health=None, planner=None, execution=None, captured_at=None) -> dict:
    """Build a canonical read-only GPTMEAi status snapshot."""
    return {
        "version": SNAPSHOT_VERSION,
        "source": SNAPSHOT_SOURCE,
        "status": derive_snapshot_status(health, planner, execution),
        "captured_at": captured_at or _utc_now(),
        "health": summarize_payload(health),
        "planner": summarize_payload(planner),
        "execution": summarize_payload(execution),
        "metadata": {
            "dry_run": True,
            "read_only": True,
            "live_required": False,
        },
    }
