"""Bridge contract validator facade."""

from __future__ import annotations

from typing import Any, Mapping

from .semascript_validator import validate_action_document


class ContractValidator:
    """Validate SEMASCRIPT action documents against the bridge contract."""

    def validate(self, document: Mapping[str, Any]) -> dict[str, Any]:
        return validate_action_document(dict(document))
