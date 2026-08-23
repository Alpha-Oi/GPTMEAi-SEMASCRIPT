"""Canonical artifact resolver."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .balance_model import BalanceModel
from .trust_model import TrustModel


class CanonicalResolver:
    """Resolve a single canonical artifact for a type."""

    def __init__(self, trust_model: TrustModel | None = None, balance_model: BalanceModel | None = None):
        self.trust_model = trust_model or TrustModel()
        self.balance_model = balance_model or BalanceModel()

    def resolve(self, artifact_type: str, artifacts: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        candidates = [dict(artifact) for artifact in artifacts if artifact.get("type") == artifact_type]
        filtered_out = []
        eligible = []

        for artifact in candidates:
            reason = self._ineligible_reason(artifact)
            if reason:
                filtered_out.append({"artifact_id": artifact.get("id"), "reason": reason})
            else:
                eligible.append(artifact)

        if not eligible:
            return {
                "artifact_id": None,
                "status": "DEFERRED",
                "input_candidates": [item.get("id") for item in candidates],
                "filtered_out": filtered_out,
            }

        ranked = sorted(
            eligible,
            key=lambda artifact: (
                self.balance_model.final_score(artifact),
                artifact.get("state") == "ACTIVE",
                self.trust_model.score(artifact),
                int(dict(artifact.get("lineage", {})).get("depth", 0)),
                str(artifact.get("id", "")),
            ),
            reverse=True,
        )
        selected = ranked[0]
        return {
            "artifact_id": selected["id"],
            "status": "SELECTED",
            "input_candidates": [item.get("id") for item in candidates],
            "filtered_out": filtered_out,
            "ranking_steps": [item.get("id") for item in ranked],
        }

    def _ineligible_reason(self, artifact: Mapping[str, Any]) -> str | None:
        if dict(artifact.get("integrity", {})).get("validated") is not True:
            return "integrity.validated != true"
        if not self.trust_model.is_eligible(artifact):
            return "trust below medium"
        if artifact.get("state") in {"UNTRUSTED", "ARCHIVED"}:
            return "lifecycle state is not canonical eligible"
        return None
