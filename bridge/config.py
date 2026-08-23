"""Configuration for the GPTMEAi-SEMASCRIPT bridge."""

import os
from dataclasses import dataclass


def _parse_bool(name, default, environ):
    value = environ.get(name)
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean-like value")


@dataclass(frozen=True)
class BridgeConfig:
    gptmeai_base_url: str = "http://127.0.0.1:8010"
    dry_run: bool = True
    require_approval: bool = True


def load_config(environ=None):
    source = os.environ if environ is None else environ
    return BridgeConfig(
        gptmeai_base_url=source.get("GPTMEAI_BASE_URL", "http://127.0.0.1:8010").rstrip("/"),
        dry_run=_parse_bool("GPTMEAI_SEMASCRIPT_DRY_RUN", True, source),
        require_approval=_parse_bool("GPTMEAI_SEMASCRIPT_REQUIRE_APPROVAL", True, source),
    )


CONFIG = load_config()
GPTMEAI_BASE_URL = CONFIG.gptmeai_base_url
DRY_RUN = CONFIG.dry_run
REQUIRE_APPROVAL = CONFIG.require_approval
