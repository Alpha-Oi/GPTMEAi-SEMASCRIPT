# Contract Compatibility Matrix

## Scope

This matrix documents GPTMEAi-SEMASCRIPT v0.1 compatibility only. v0.1 is
dry-run, preview-only, and read-only. It validates or normalizes SEMASCRIPT
inputs, maps them into a GPTMEAi planner preview, and requires approval before
any future execution design. It does not execute actions or mutate source
projects, memory, storage, runtime, or ledgers.

The machine-readable companion is
`contracts/compatibility_matrix.v0.1.json`.

## SEMASCRIPT AST Compatibility

| Field / Concept | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `version` | supported | `schema_version` | Preserved as action document `metadata.schema_version`. | Fixture uses `SEMASCRIPT_AST_SCHEMA_v0.1`. |
| `kind/type` | supported | `ast.kind`, `ast.class_name`, `ast.root` | Maps into intent summary, action type, and action inputs. | `EXEC:OBSERVE` maps to safe `observe`, not execution. |
| `source` | preserved | `source_profile`, `source_text` | `source_profile` maps to source/constraints; `source_text` maps to metadata. | Source text is not executed. |
| `intent` | supported | explicit `intent`, `summary`, `goal`, or AST fallback | Normalized to canonical `intent.summary`. | Empty intent gets a safe normalization label. |
| `actions` | supported | `actions`, `steps`, or AST root node | Normalized to canonical `actions[]`. | AST root becomes one preview action. |
| `action id` | supported | `action.id` or generated index | Preserved or defaulted to `action-N`. | AST root fixture uses `ast-root-1`. |
| `action type` | supported | `action.type`, `operation`, or safe AST mapping | Preserved for action documents; AST `EXEC` roots map through a safe allowlist. | Risky types only produce preview risks. |
| `action target` | preserved | AST roles such as `obj` and `res` | Preserved under `actions[].inputs.roles`; no execution binding. | No target dereference in v0.1. |
| `action payload` | preserved | `inputs`, AST roles, AST modifiers | Preserved as planner preview inputs. | Preview-only payload. |
| `constraints` | supported | `constraints` or AST-derived flags | Normalized to canonical constraints object. | Shape validated; not mapped into execution. |
| `safety` | required | input safety or adapter defaults | Requires `dry_run_only: true` and `requires_approval: true`. | Missing `forbidden_operations` is a warning, not a hard error. |
| `metadata` | preserved | input metadata and validation annotations | Preserved with `normalized_from` marker. | No secrets or runtime data should be placed here. |
| graph/session references | ignored-safe | SEMASCRIPT graph/session concepts | May be preserved in metadata or inputs but not interpreted. | Planned richer compatibility in v0.2. |
| state references | ignored-safe | SEMASCRIPT state references | May be preserved but never dereferenced or mutated. | No state mutation in v0.1. |
| lineage references | ignored-safe | SEMASCRIPT lineage references | May be preserved but never written. | Outcome lineage mapping is future work. |
| execution/runtime fields | unsupported-v0.1 | Runtime execution concepts | Not executed; represented only as dry-run risks or forbidden operations. | Execution enablement is outside v0.1. |

## SEMASCRIPT Action Document Compatibility

| Field | Required / Optional | Validation Behavior | Mapping Behavior | Failure Behavior |
| --- | --- | --- | --- | --- |
| `version` | required | Must be a non-empty string. | Bridge emits planner preview version `0.1`; input version is validated but not copied into preview version. | Validation error. |
| `source` | required | Must be an object with `source.system == "SEMASCRIPT"`. | `source.system` and `source.document_id` map into preview metadata. | Validation error. |
| `intent` | required | Must be an object with non-empty `intent.summary`. | `intent.summary` maps into preview metadata `intent_summary`. | Validation error. |
| `actions[]` | required | Must be a non-empty array; each action requires `id`, `type`, and `description`. | Each action maps to `mapped_actions[]` with dry-run execution mode. | Validation error. |
| `constraints` | required | Must be an object. | Validated for shape; not consumed by the preview mapper in v0.1. | Validation error. |
| `safety` | required | Must be an object; `dry_run_only` and `requires_approval` must be `true`. | Enforces dry-run and approval gate behavior. | Validation error. |
| `metadata` | required | Must be an object. | Preserved only when adapter code explicitly reads a key. | Validation error. |

## GPTMEAi Status / Sample Compatibility

### `/health` Sample

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `status` | supported | `gptmeai_health.sample.json` | Fixture expects `ok`. | Read-only sample. |
| `service` | supported | `gptmeai_health.sample.json` | Fixture expects `AI OS API`. | Read-only sample. |
| `planner_active` | supported | `gptmeai_health.sample.json` | Presence checked by compatibility tests. | No planner mutation. |
| `execution_failed` | supported | `gptmeai_health.sample.json` | Presence checked by compatibility tests. | No execution mutation. |
| `memory_count` | preserved | `gptmeai_health.sample.json` | Sample field only. | Never mutated. |

### `/planner/status` Sample

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `status` | supported | `gptmeai_planner_status.sample.json` | Fixture expects `ok`. | Read-only sample. |
| `service` | supported | `gptmeai_planner_status.sample.json` | Identifies planner runtime status payload. | No live runtime required. |
| `plan_counts` | supported | `gptmeai_planner_status.sample.json` | Presence checked by tests. | No writes. |
| `step_counts` | supported | `gptmeai_planner_status.sample.json` | Presence checked by tests. | No writes. |
| `plans` | supported | `gptmeai_planner_status.sample.json` | Presence checked by tests. | Static sample only. |
| `events` | preserved | `gptmeai_planner_status.sample.json` | Not consumed by the mapper. | Future compatibility candidate. |

### `/execution/status` Sample

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `status` | supported | `gptmeai_execution_status.sample.json` | Fixture expects `ok`. | Read-only sample. |
| `service` | supported | `gptmeai_execution_status.sample.json` | Identifies execution runtime status payload. | Status read does not enable execution. |
| `operation_counts` | supported | `gptmeai_execution_status.sample.json` | Presence checked by tests. | No operation writes. |
| `compensation_counts` | supported | `gptmeai_execution_status.sample.json` | Presence checked by tests. | No compensation writes. |
| `operations` | supported | `gptmeai_execution_status.sample.json` | Presence checked as static read-only sample. | No execution dispatch. |
| `lineage` | preserved | `gptmeai_execution_status.sample.json` | Sample field only. | Never written by bridge. |

## GPTMEAi Readonly Status Snapshot Compatibility

This is a v0.2-prep, read-only contract. It is not required for v0.1 local
verification and does not change the v0.1 dry-run boundary.

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `version` | planned-v0.2 | snapshot schema | Snapshot contract version, currently `0.2-prep`. | Required by schema. |
| `source` | planned-v0.2 | mapper | Constant `gptmeai` source marker. | Read-only marker. |
| `status` | planned-v0.2 | mapper | `ok`, `degraded`, `unavailable`, or `unknown` from section availability. | No live runtime required. |
| `captured_at` | planned-v0.2 | mapper or fixture | ISO-style capture timestamp or deterministic fixture timestamp. | Metadata only. |
| `health` | planned-v0.2 | `/health` payload or fixture | Summarizes availability, top-level keys, and payload. | No mutation. |
| `planner` | planned-v0.2 | `/planner/status` payload or fixture | Summarizes availability, top-level keys, and payload. | No planner mutation. |
| `execution` | planned-v0.2 | `/execution/status` payload or fixture | Summarizes availability, top-level keys, and payload. | Status only; no execution enablement. |
| `metadata` | planned-v0.2 | mapper | Sets `dry_run: true`, `read_only: true`, and `live_required: false`. | Safety flags. |

## Planner Preview Output Compatibility

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `version` | required | mapper | Bridge planner preview contract version, currently `0.1`. | Required by schema. |
| `preview_id` | supported | generated | Uses `preview-<uuid>`. | New per preview. |
| `status` | supported | mapper | `preview` for successful v0.1 mapping. | `rejected` appears in schema for future approval paths. |
| `mapped_actions[]` | supported | `actions[]` | Maps `id`, `type`, `description`, `inputs`, and `expected_output`. | Each mapped action has `execution_mode: dry_run`. |
| `required_approvals[]` | required | mapper | Always includes an `execution_approval` requirement. | Approval object is local only in v0.1. |
| `risks[]` | supported | mapper | Always includes dry-run risk; risky action types add medium risk. | Risk does not execute anything. |
| `dry_run` | required | mapper/config contract | Always `true`. | Required by schema and tests. |
| `metadata` | supported | source, intent, validation, config | Includes adapter name, timestamp, source fields, intent summary, action count, config flags, warnings. | Metadata is not a runtime write. |

## Execution Approval Compatibility

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `approval_id` | planned-v0.2 | approval schema | Tracked as local approval object identity. | Does not enable execution. |
| `preview_id` | supported | approval schema | References the planner preview under review. | Local object logic only. |
| `approved` | planned-v0.2 | approval schema | Tracked for future approval handoff design. | Approval records do not execute in v0.1. |
| `approved_by` | planned-v0.2 | approval schema | Tracked for future approval audit metadata. | No auth integration in v0.1. |
| `scope` | planned-v0.2 | approval schema | Tracked for future bounded approval scope. | No runtime dispatch. |
| `expires_at` | planned-v0.2 | approval schema | Tracked for future approval expiry. | No scheduler/runtime mutation. |
| `metadata` | preserved | approval schema | Local approval metadata only. | Must not contain secrets. |

## Adapter Error Model Compatibility

| Field | Status | Source | Bridge Handling | Notes |
| --- | --- | --- | --- | --- |
| `error_code` | supported | error schema | Stable machine-readable error identifier. | Used for adapter/validation failures. |
| `message` | supported | error schema | Human-readable validation or adapter message. | No secrets. |
| `severity` | supported | error schema | `info`, `warning`, `error`, or `critical`. | Mirrors schema enum. |
| `source` | supported | error schema | Originating bridge component or contract surface. | Diagnostic only. |
| `retryable` | supported | error schema | Indicates whether retry is safe. | No automatic retry runtime. |
| `details` | preserved | error schema | Structured details object. | Must not include secrets or runtime data. |

## Explicit Non-Support In v0.1

- real execution
- memory mutation
- storage mutation
- ledger mutation
- runtime mutation
- live GPTMEAi availability requirement
- UI merge
- dependency installation

## Test Coverage Mapping

| Compatibility Rule | Test Coverage |
| --- | --- |
| Action document required fields and manual validation | `tests/test_contracts.py` |
| Valid/invalid action document behavior | `tests/test_contracts.py` |
| Dry-run planner preview and approval requirement | `tests/test_dry_run_adapter.py` |
| GPTMEAi client remains read-only and exposes no `execute` method | `tests/test_dry_run_adapter.py`, `tests/test_compatibility_fixtures.py` |
| SEMASCRIPT AST fixture normalizes into expected action document | `tests/test_compatibility_fixtures.py` |
| GPTMEAi status fixtures are static read-only shapes | `tests/test_compatibility_fixtures.py` |
| Root reports and protected folders are blocked | `tests/test_root_cleanliness.py` |
| Local verification wrapper runs safe checks in order | `tests/test_local_verification_wrapper.py` |
| Compatibility matrix JSON, loader, unsupported boundaries | `tests/test_contract_compatibility_matrix.py` |
