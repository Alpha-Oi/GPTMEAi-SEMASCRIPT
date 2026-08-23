"""Write a read-only Artifact OS checkpoint summary.

The tool reads reports/codex/ARTIFACT_INDEX.json and selected existing
verification reports, then writes reports/codex/ARTIFACT_OS_CHECKPOINT_SUMMARY.md.
It does not modify ARTIFACT_INDEX.json or call live runtimes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CHECKPOINT_FILENAME = "ARTIFACT_OS_CHECKPOINT_SUMMARY.md"
INDEX_PATH = Path("reports") / "codex" / "ARTIFACT_INDEX.json"
OUTPUT_PATH = Path("reports") / "codex" / CHECKPOINT_FILENAME
REGISTRATION_REPORT = Path("reports") / "codex" / "GOVERNED_LIFECYCLE_SMOKE_ARTIFACT_REGISTRATION_REPORT.md"
SMOKE_REPORT = Path("reports") / "codex" / "GOVERNED_LIFECYCLE_SMOKE_REPORT.md"
LOCAL_WRAPPER_REPORT = Path("reports") / "codex" / "LOCAL_SMOKE_WRAPPER_REPORT.md"
SOURCE_MANIFEST = Path("source_references") / "MANIFEST.md"
GOVERNED_SMOKE_ARTIFACT_ID = "governed-lifecycle-smoke-test::1.0::2026-05-27"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def read_optional_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def bullet(value: str) -> str:
    return f"- {value}"


def code(value: Any) -> str:
    return f"`{value}`"


def sorted_artifacts(index: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = [item for item in as_list(index.get("artifacts")) if isinstance(item, dict)]
    return sorted(artifacts, key=lambda item: str(item.get("id", "")))


def canonical_artifact_map(index: dict[str, Any]) -> dict[str, str]:
    governance_engine = as_dict(index.get("governance_engine"))
    resolver = as_dict(governance_engine.get("canonical_resolver"))
    mapping = as_dict(resolver.get("canonical_by_type"))
    return {str(key): str(value) for key, value in sorted(mapping.items())}


def governed_smoke_artifact(index: dict[str, Any]) -> dict[str, Any] | None:
    for artifact in sorted_artifacts(index):
        if artifact.get("id") == GOVERNED_SMOKE_ARTIFACT_ID:
            return artifact
    for artifact in sorted_artifacts(index):
        if artifact.get("type") == "system_verification_artifact":
            return artifact
    return None


def lineage_chain(index: dict[str, Any]) -> list[str]:
    smoke = governed_smoke_artifact(index)
    if smoke:
        lineage = as_dict(smoke.get("lineage"))
        chain = [str(item) for item in as_list(lineage.get("chain"))]
        if chain:
            return chain
    canonical = canonical_artifact_map(index)
    preferred_types = [
        "architecture_map",
        "system_consistency_contract_layer",
        "system_decomposition_mode",
        "implementation_root_skeleton",
        "executable_runtime_node",
        "observability_governance_layer",
        "governed_response_layer",
        "governed_enforcement_layer",
        "system_verification_artifact",
    ]
    return [canonical[item] for item in preferred_types if item in canonical]


def format_constraints(index: dict[str, Any]) -> list[str]:
    constraints = as_dict(index.get("constraints"))
    if not constraints:
        return [bullet("none recorded")]
    return [bullet(f"{key}: {code(value)}") for key, value in sorted(constraints.items())]


def format_canonical_artifacts(index: dict[str, Any]) -> list[str]:
    mapping = canonical_artifact_map(index)
    if not mapping:
        return [bullet("none recorded")]
    return [bullet(f"{artifact_type}: {code(artifact_id)}") for artifact_type, artifact_id in mapping.items()]


def format_active_artifacts(index: dict[str, Any]) -> list[str]:
    active = [
        artifact
        for artifact in sorted_artifacts(index)
        if artifact.get("state") == "ACTIVE" or artifact.get("status") in {"ACTIVE", "CANONICAL"}
    ]
    if not active:
        return [bullet("none recorded")]
    lines = []
    for artifact in active:
        lines.append(
            bullet(
                f"{code(artifact.get('id', 'unknown'))} "
                f"type={code(artifact.get('type', 'unknown'))} "
                f"state={code(artifact.get('state', 'unknown'))} "
                f"status={code(artifact.get('status', 'unknown'))}"
            )
        )
    return lines


def find_verification_markers(text_by_name: dict[str, str]) -> list[str]:
    combined = "\n".join(text_by_name.values())
    checks = [
        ("4 tests OK", ("4 tests OK", "Ran 4 tests")),
        ("107 tests OK", ("107 tests OK", "Ran 107 tests")),
        ("7 tests OK", ("7 tests OK", "Ran 7 tests")),
        ("VERIFY_BRIDGE=OK", ("VERIFY_BRIDGE=OK",)),
        ("ROOT_CLEANLINESS=OK", ("ROOT_CLEANLINESS=OK",)),
    ]
    markers = []
    for label, patterns in checks:
        found_in = [name for name, text in text_by_name.items() if any(pattern in text for pattern in patterns)]
        if found_in:
            markers.append(f"- `{label}` found in {', '.join(sorted(found_in))}")
        else:
            markers.append(f"- `{label}` not found in inspected reports")
    return markers


def source_reference_summary(manifest_text: str) -> list[str]:
    if not manifest_text:
        return [bullet("source_references\\MANIFEST.md not found")]
    lines = []
    for label in (
        "Generated",
        "Target root",
        "GPTMEAi source root",
        "SEMASCRIPT source root",
        "Source mode",
        "Files copied from source projects",
    ):
        match = re.search(rf"^- {re.escape(label)}: (.+)$", manifest_text, re.MULTILINE)
        if match:
            lines.append(bullet(f"{label}: {match.group(1)}"))
    missing = re.search(r"^- Missing / not found entries: (\d+)$", manifest_text, re.MULTILINE)
    if missing:
        lines.append(bullet(f"Missing / not found entries: `{missing.group(1)}`"))
    if not lines:
        return [bullet("source_references\\MANIFEST.md present, but expected summary fields were not found")]
    return lines


def governed_smoke_lines(artifact: dict[str, Any] | None) -> list[str]:
    if not artifact:
        return [bullet("governed lifecycle smoke artifact not found")]
    verification = as_dict(artifact.get("verification"))
    runtime_binding = as_dict(artifact.get("runtime_binding"))
    lines = [
        bullet(f"Artifact ID: {code(artifact.get('id', 'unknown'))}"),
        bullet(f"Type: {code(artifact.get('type', 'unknown'))}"),
        bullet(f"Date: {code(artifact.get('date', 'unknown'))}"),
        bullet(f"State: {code(artifact.get('state', 'unknown'))}"),
        bullet(f"Status: {code(artifact.get('status', 'unknown'))}"),
        bullet(f"Path: {code(artifact.get('path', 'unknown'))}"),
        bullet(f"Source report: {code(artifact.get('source_report', 'unknown'))}"),
        bullet(f"Runtime mutation: {code(runtime_binding.get('runtime_mutation', 'unknown'))}"),
        bullet(f"Artifact index mutation: {code(runtime_binding.get('artifact_index_mutation', 'unknown'))}"),
    ]
    if verification:
        lines.append(bullet("Verification: " + ", ".join(f"{key}={value}" for key, value in sorted(verification.items()))))
    return lines


def build_markdown(root: Path, index: dict[str, Any], text_by_name: dict[str, str], manifest_text: str) -> str:
    artifacts = sorted_artifacts(index)
    events = as_list(index.get("event_log"))
    smoke_artifact = governed_smoke_artifact(index)
    chain = lineage_chain(index)

    lines: list[str] = [
        "# ARTIFACT_OS_CHECKPOINT_SUMMARY.md",
        "",
        "## Purpose",
        "This checkpoint is a read-only baseline summary before Stage 4 functional integration.",
        "It summarizes the current Artifact OS registry and verification evidence without modifying `ARTIFACT_INDEX.json`, source projects, runtime state, memory, storage, ledger, or source references.",
        "",
        "## Project stage",
        "Stage 3 — Bridge stabilized with smoke/check artifacts.",
        "",
        "## Registry source",
        str(root / INDEX_PATH),
        "",
        "## Registry summary",
        bullet(f"Version: {code(index.get('version', 'unknown'))}"),
        bullet(f"Artifact count: {code(len(artifacts))}"),
        bullet(f"Event count: {code(len(events))}"),
        "- Constraints:",
    ]
    lines.extend(f"  {line}" for line in format_constraints(index))
    lines.extend(
        [
            "",
            "## Canonical artifacts",
        ]
    )
    lines.extend(format_canonical_artifacts(index))
    lines.extend(
        [
            "",
            "## Active/current artifacts",
        ]
    )
    lines.extend(format_active_artifacts(index))
    lines.extend(
        [
            "",
            "## Canonical artifact lineage",
        ]
    )
    if chain:
        lines.extend(bullet(f"{position}. {code(artifact_id)}") for position, artifact_id in enumerate(chain, start=1))
    else:
        lines.append(bullet("canonical lineage chain not found"))
    lines.extend(
        [
            "",
            "## Governed lifecycle smoke binding",
        ]
    )
    lines.extend(governed_smoke_lines(smoke_artifact))
    lines.extend(
        [
            "",
            "## Last green verification evidence",
        ]
    )
    lines.extend(find_verification_markers(text_by_name))
    lines.extend(
        [
            "",
            "## Bridge boundary",
            "- bridge/adapter project",
            "- dry-run/preview-only",
            "- not merged runtime",
            "- no live GPTMEAi execution",
            "- no SEMASCRIPT runtime/session mutation",
            "- no GPTMEAi memory, storage, ledger, snapshot, or execution-state mutation",
            "",
            "## Source reference status",
        ]
    )
    lines.extend(source_reference_summary(manifest_text))
    lines.extend(
        [
            "",
            "## Risks preserved for next stage",
            "- Do not treat this bridge as a merged GPTMEAi + SEMASCRIPT runtime.",
            "- Keep `reports/codex/ARTIFACT_INDEX.json` as the observed canonical registry location; root `ARTIFACT_INDEX.json` is absent.",
            "- Preserve the dry-run, preview-only, approval-gated boundary before any Stage 4 functional integration.",
            "- Do not rely on optional live GPTMEAi availability; previous verification allowed `/health` timeout as non-fatal.",
            "- Distinguish local governance/bootstrap skeleton behavior from real GPTMEAi or SEMASCRIPT runtime behavior.",
            "- Refresh full local verification before promoting any functional integration step.",
            "",
            "## Recommended next step",
            "Run a fresh required local verification baseline with `python -B tools\\run_local_verification.py` and compare it against this checkpoint before starting Stage 4 functional integration design.",
            "",
        ]
    )
    return "\n".join(lines)


def write_checkpoint(root: Path) -> Path:
    index_path = root / INDEX_PATH
    index = read_json(index_path)
    text_by_name = {
        "GOVERNED_LIFECYCLE_SMOKE_ARTIFACT_REGISTRATION_REPORT.md": read_optional_text(root, REGISTRATION_REPORT),
        "GOVERNED_LIFECYCLE_SMOKE_REPORT.md": read_optional_text(root, SMOKE_REPORT),
        "LOCAL_SMOKE_WRAPPER_REPORT.md": read_optional_text(root, LOCAL_WRAPPER_REPORT),
    }
    manifest_text = read_optional_text(root, SOURCE_MANIFEST)
    output = root / OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_markdown(root, index, text_by_name, manifest_text), encoding="utf-8")
    return output


def main() -> int:
    root = project_root()
    output = write_checkpoint(root)
    print(f"ARTIFACT_OS_CHECKPOINT_SUMMARY={output}")
    print("CHECKPOINT_STATUS=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
