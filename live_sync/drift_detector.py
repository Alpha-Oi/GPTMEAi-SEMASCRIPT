"""Deterministic drift detection between ARTIFACT OS and runtime observations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


DRIFT_LEVEL_ORDER = {
    "NO_DRIFT": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


class DriftDetector:
    """Compare governed artifact state with observed executable runtime state.

    The detector does not modify either side. It stores the last comparison only
    to support the no-argument detector methods requested by the layer contract.
    """

    def __init__(self):
        self._artifact_state: dict[str, Any] = {}
        self._runtime_state: dict[str, Any] = {}
        self._last_details: dict[str, Any] = {}

    def compare_artifact_vs_runtime(
        self,
        artifact_state: Mapping[str, Any],
        runtime_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        self._artifact_state = deepcopy(dict(artifact_state))
        self._runtime_state = deepcopy(dict(runtime_state))

        details = {
            "structural": self.detect_structural_drift(),
            "behavioral": self.detect_behavioral_drift(),
            "event": self.detect_event_drift(),
            "governance": self.detect_governance_drift(),
            "lineage": self.detect_lineage_drift(),
        }
        self._last_details = details
        return self.generate_drift_report()

    def detect_structural_drift(self) -> dict[str, Any]:
        expected = set(self._artifact_state.get("expected_modules", []))
        observed = set(self._runtime_state.get("observed_modules", []))
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        return {
            "drift": bool(missing or extra),
            "level": "HIGH" if missing else ("MEDIUM" if extra else "NO_DRIFT"),
            "missing_modules": missing,
            "extra_modules": extra,
            "affected_layer": "runtime_structure",
        }

    def detect_behavioral_drift(self) -> dict[str, Any]:
        expected = list(self._artifact_state.get("expected_flow", []))
        observed = list(self._runtime_state.get("observed_flow", []))
        missing_steps = [step for step in expected if step not in observed]
        order_mismatch = bool(not missing_steps and expected and observed and expected != observed)
        return {
            "drift": bool(missing_steps or order_mismatch),
            "level": "HIGH" if missing_steps else ("MEDIUM" if order_mismatch else "NO_DRIFT"),
            "missing_steps": missing_steps,
            "order_mismatch": order_mismatch,
            "expected_flow": expected,
            "observed_flow": observed,
            "affected_layer": "runtime_behavior",
        }

    def detect_event_drift(self) -> dict[str, Any]:
        artifact_events = list(self._artifact_state.get("artifact_event_ids", []))
        runtime_events = list(self._runtime_state.get("runtime_event_ids", []))
        artifact_set = set(artifact_events)
        runtime_set = set(runtime_events)
        duplicated = sorted(
            event_id for event_id in runtime_set if runtime_events.count(event_id) > 1
        )
        missing = sorted(artifact_set - runtime_set)
        extra = sorted(runtime_set - artifact_set)
        drift = bool(missing or extra or duplicated)
        return {
            "drift": drift,
            "level": "CRITICAL" if duplicated else ("HIGH" if missing else ("MEDIUM" if extra else "NO_DRIFT")),
            "missing_runtime_events": missing,
            "extra_runtime_events": extra,
            "duplicated_runtime_events": duplicated,
            "affected_layer": "event_store",
        }

    def detect_governance_drift(self) -> dict[str, Any]:
        markers = dict(self._runtime_state.get("governance_markers", {}))
        expected_true = (
            "risk_before_governance",
            "governance_before_validation",
            "validation_before_execution",
            "execution_boundary_present",
        )
        failed = sorted(marker for marker in expected_true if markers.get(marker) is not True)
        return {
            "drift": bool(failed),
            "level": "CRITICAL" if failed else "NO_DRIFT",
            "failed_markers": failed,
            "affected_layer": "governance",
        }

    def detect_lineage_drift(self) -> dict[str, Any]:
        artifact_chain = list(self._artifact_state.get("lineage_chain", []))
        runtime_chain = list(self._runtime_state.get("lineage_chain", []))
        return {
            "drift": artifact_chain != runtime_chain,
            "level": "HIGH" if artifact_chain != runtime_chain else "NO_DRIFT",
            "artifact_lineage": artifact_chain,
            "runtime_lineage": runtime_chain,
            "affected_layer": "lineage",
        }

    def generate_drift_report(self) -> dict[str, Any]:
        drift_types = []
        affected_layers = []
        max_level = "NO_DRIFT"

        type_map = {
            "structural": "STRUCTURAL_DRIFT",
            "behavioral": "BEHAVIORAL_DRIFT",
            "event": "EVENT_DRIFT",
            "governance": "GOVERNANCE_DRIFT",
            "lineage": "LINEAGE_DRIFT",
        }

        for key in ("structural", "behavioral", "event", "governance", "lineage"):
            detail = self._last_details.get(key, {})
            if detail.get("drift"):
                drift_types.append(type_map[key])
                affected_layers.append(detail.get("affected_layer", key))
                level = detail.get("level", "LOW")
                if DRIFT_LEVEL_ORDER[level] > DRIFT_LEVEL_ORDER[max_level]:
                    max_level = level

        if not drift_types:
            max_level = "LOW"

        return {
            "drift_status": "DRIFT_DETECTED" if drift_types else "NO_DRIFT",
            "drift_level": max_level,
            "drift_types": drift_types,
            "affected_layers": sorted(set(affected_layers)),
            "recommended_action": self._recommended_action(drift_types, max_level),
            "requires_governance_review": bool(drift_types),
            "details": deepcopy(self._last_details),
        }

    def _recommended_action(self, drift_types: list[str], level: str) -> str:
        if not drift_types:
            return "No action required; continue deterministic monitoring."
        if level in {"HIGH", "CRITICAL"}:
            return "Open governance review before runtime or artifact changes."
        return "Record drift report and review in the next bounded maintenance slice."
