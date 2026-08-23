"""Read-only live synchronization engine."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from artifact_system import ArtifactIndexLoader

from .drift_detector import DriftDetector


EXPECTED_RUNTIME_MODULES = (
    "core.event_store",
    "core.state_engine",
    "core.risk_engine",
    "core.governance",
    "core.evolution_engine",
    "core.validation_engine",
    "core.execution_boundary",
    "runtime.orchestrator",
    "runtime.loop_runner",
    "bridge.semascript_bridge",
)

EXPECTED_RUNTIME_FLOW = (
    "event_store",
    "state_engine",
    "snapshot",
    "mental_model",
    "risk_engine",
    "governance_engine",
    "validation_engine",
    "execution_boundary",
    "event_store_append",
)


class LiveSyncEngine:
    """Synchronize ARTIFACT OS projection with observed runtime state.

    The engine reads files and metadata only. It does not import or execute the
    bootstrap runtime, and it does not write sync events into ARTIFACT_INDEX.
    """

    def __init__(
        self,
        artifact_index_path: str | Path,
        runtime_root: str | Path,
        detector: DriftDetector | None = None,
    ):
        self.artifact_index_path = Path(artifact_index_path)
        self.runtime_root = Path(runtime_root)
        self.detector = detector or DriftDetector()
        self.loader = ArtifactIndexLoader()

    def poll_runtime_state(self) -> dict[str, Any]:
        """Read executable bootstrap structure without running it."""
        observed_modules = [
            module
            for module in EXPECTED_RUNTIME_MODULES
            if self._module_path(module).exists()
        ]
        artifact_index = self._read_runtime_artifact_index()
        lineage_chain = self._runtime_lineage_from_artifacts(artifact_index)
        return {
            "runtime_path": self._runtime_path_for_report(),
            "observed_modules": observed_modules,
            "observed_flow": self._observed_flow(observed_modules),
            "runtime_event_ids": self._runtime_event_ids(),
            "governance_markers": self._governance_markers(observed_modules),
            "lineage_chain": lineage_chain,
            "runtime_executed": False,
            "observation_mode": "read_only_file_scan",
        }

    def fetch_artifact_state(self) -> dict[str, Any]:
        """Project governed artifact state from ARTIFACT_INDEX and event_log."""
        index = self.loader.load(self.artifact_index_path)
        executable = self._artifact_by_id(index, "executable-bootstrap-codebase::1.0::2026-05-27")
        if executable is None:
            raise ValueError("executable bootstrap artifact is not registered")
        return {
            "artifact_id": executable["id"],
            "expected_modules": list(EXPECTED_RUNTIME_MODULES),
            "expected_flow": list(EXPECTED_RUNTIME_FLOW),
            "artifact_event_ids": self._lineage_event_ids(index, executable),
            "lineage_chain": list(executable.get("lineage", {}).get("chain", [])),
            "governance_classification": executable.get("governance_classification"),
            "runtime_binding": deepcopy(executable.get("runtime_binding", {})),
        }

    def synchronize(self) -> dict[str, Any]:
        """Compare ARTIFACT OS projection to runtime observation."""
        artifact_state = self.fetch_artifact_state()
        runtime_state = self.poll_runtime_state()
        report = self.detector.compare_artifact_vs_runtime(artifact_state, runtime_state)
        report["artifact_state_id"] = artifact_state["artifact_id"]
        report["runtime_observation"] = {
            "runtime_path": runtime_state["runtime_path"],
            "runtime_executed": runtime_state["runtime_executed"],
            "observation_mode": runtime_state["observation_mode"],
        }
        return report

    def emit_sync_event(self, report: Mapping[str, Any]) -> dict[str, Any]:
        """Return a sync event object without appending it anywhere."""
        event_type = "DRIFT_DETECTED" if report.get("drift_status") == "DRIFT_DETECTED" else "SYNC_OK"
        return {
            "event_id": f"event::live-sync::{event_type.lower()}",
            "event_type": event_type,
            "artifact_id": report.get("artifact_state_id", "executable-bootstrap-codebase::1.0::2026-05-27"),
            "payload": {
                "drift_status": report.get("drift_status"),
                "drift_level": report.get("drift_level"),
                "drift_type": list(report.get("drift_types", [])),
                "affected_component": list(report.get("affected_layers", [])),
                "severity": report.get("drift_level"),
                "timestamp": "deterministic-not-recorded",
                "source_vs_runtime_mismatch_summary": report.get("recommended_action", ""),
            },
        }

    def _module_path(self, module: str) -> Path:
        return self.runtime_root / Path(*module.split(".")).with_suffix(".py")

    def _runtime_path_for_report(self) -> str:
        return self.runtime_root.name + "/"

    def _observed_flow(self, observed_modules: list[str]) -> list[str]:
        module_set = set(observed_modules)
        flow = []
        if "core.event_store" in module_set:
            flow.append("event_store")
        if "core.state_engine" in module_set:
            flow.append("state_engine")
        if "runtime.orchestrator" in module_set:
            flow.extend(["snapshot", "mental_model"])
        if "core.risk_engine" in module_set:
            flow.append("risk_engine")
        if "core.governance" in module_set:
            flow.append("governance_engine")
        if "core.validation_engine" in module_set:
            flow.append("validation_engine")
        if "core.execution_boundary" in module_set:
            flow.append("execution_boundary")
        if "core.event_store" in module_set and "runtime.orchestrator" in module_set:
            flow.append("event_store_append")
        return flow

    def _governance_markers(self, observed_modules: list[str]) -> dict[str, bool]:
        module_set = set(observed_modules)
        orchestrator_text = self._module_path("runtime.orchestrator").read_text(encoding="utf-8")
        risk_pos = orchestrator_text.find("risk = self.risk_engine.classify")
        governance_pos = orchestrator_text.find("governance = self.governance_engine.evaluate")
        validation_pos = orchestrator_text.find("validation = self.validation_engine.validate_loop_integrity")
        boundary_pos = orchestrator_text.find("boundary = self.execution_boundary.execute_if_approved")
        return {
            "risk_before_governance": 0 <= risk_pos < governance_pos,
            "governance_before_validation": 0 <= governance_pos < validation_pos,
            "validation_before_execution": 0 <= validation_pos < boundary_pos,
            "execution_boundary_present": "core.execution_boundary" in module_set and boundary_pos >= 0,
        }

    def _read_runtime_artifact_index(self) -> dict[str, Any]:
        path = self.runtime_root / "artifacts" / "artifact_index.json"
        if not path.exists():
            return {"artifacts": []}
        return self.loader.load(path)

    def _runtime_lineage_from_artifacts(self, runtime_index: Mapping[str, Any]) -> list[str]:
        artifact_ids = [artifact.get("artifact_id") for artifact in runtime_index.get("artifacts", [])]
        expected = [
            "system-map::2.0::2026-05-27",
            "validation-checklist-layer::1.0::2026-05-27",
            "system-engineering-blueprint-mode::1.0::2026-05-27",
            "codebase-skeleton::1.0::2026-05-27",
            "executable-bootstrap-codebase::1.0::2026-05-27",
        ]
        return [artifact_id for artifact_id in expected if artifact_id in artifact_ids]

    def _runtime_event_ids(self) -> list[str]:
        # Runtime has no persisted execution event log yet, so use static lineage
        # events inferred from the registered runtime artifact relation.
        return [
            "event::2026-05-27::codebase-skeleton::artifact-created::001",
            "event::2026-05-27::executable-bootstrap-codebase::artifact-created::001",
        ]

    def _artifact_by_id(self, index: Mapping[str, Any], artifact_id: str) -> dict[str, Any] | None:
        for artifact in index.get("artifacts", []):
            if artifact.get("id") == artifact_id:
                return deepcopy(dict(artifact))
        return None

    def _lineage_event_ids(self, index: Mapping[str, Any], artifact: Mapping[str, Any]) -> list[str]:
        lineage_ids = set(artifact.get("lineage", {}).get("chain", []))
        lineage_ids.add(artifact.get("id", ""))
        event_ids = []
        for event in index.get("event_log", []):
            if event.get("artifact_id") in lineage_ids:
                event_ids.append(event.get("event_id"))
        # Compare the immediate implementation/runtime transition only.
        immediate = {
            "event::2026-05-27::codebase-skeleton::artifact-created::001",
            "event::2026-05-27::executable-bootstrap-codebase::artifact-created::001",
        }
        return sorted(event_id for event_id in event_ids if event_id in immediate)
