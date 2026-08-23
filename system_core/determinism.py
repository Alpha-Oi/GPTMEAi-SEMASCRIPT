"""Deterministic serialization helpers used across architecture skeleton modules."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Return stable JSON for hashing, comparison, and replay outputs."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(value: Any) -> str:
    """Return a deterministic SHA-256 hash for JSON-compatible values."""
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest().upper()
    return f"sha256:{digest}"
