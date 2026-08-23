# Semantic Concept Layers Implementation Plan

## 1. Purpose

The goal is to add concept/reference layers to GPTMEAi-SEMASCRIPT as
read-only semantic artifacts first, not as runtime decision logic.

Semantic layers may help future Codex/ChatGPT continuation work by preserving
project vocabulary, diagnostic questions, source status, and guardrails. They
must remain subordinate to `AGENTS.md`, current files, command output, tests,
contracts, review reports, and explicit user prompts.

Current repository evidence:

- `docs\semantic_dictionaries\` is missing.
- `docs\knowledge\` exists and contains the optional GPTMAIOS Sci-Fi V4
  terminology material and its usage guard checklist.
- No repository source artifact was found for Jacque Fresco, Roger Saip, or
  Ender's Game concept dictionaries.
- `docs\11_STAGE4_PREVIEW_HANDOFF_GREEN_BASELINE.md` recommends the next slice
  as `system_thinking_dictionary_v1_ru.md` read-only reference plus guard test.

## 2. Non-goals and boundaries

Semantic concept layers must not introduce:

- runtime behavior changes;
- API changes;
- planner or dispatch changes;
- Stage 4 builder or adapter behavior changes;
- execution calls;
- live runtime startup;
- memory, storage, session, workspace, lineage, ledger, or database mutation;
- source project edits;
- dependency, environment, package, or lockfile changes;
- automatic decision-making from semantic dictionaries;
- treating books, fiction, prompts, analogies, or terminology as source of
  truth above project evidence.

The semantic layers are reference material only until a separate approved task
creates a contract, loader, status CLI, or dry-run diagnostic integration.

## 3. Source of Truth rule for semantic layers

Every concept artifact must be one of these:

- embedded in an approved Codex prompt;
- already present in repository files;
- explicitly provided as a source artifact in a safe repository path;
- marked as missing source evidence.

Extracted concepts are project reference artifacts. They are not claims of exact
quotes unless a verified source excerpt is provided. Long copyrighted passages
must not be copied. If source evidence is absent, the implementation slice must
stop at intake and document the missing source rather than inventing content.

Current source status:

- System Thinking / Jacque Fresco aligned layer: missing source evidence.
- Roger Saip concepts layer: missing source evidence.
- Roger Saip practical models layer: missing source evidence.
- Ender's Game terminology layer: missing source evidence.
- GPTMAIOS Sci-Fi V4 terminology: source exists under `docs\knowledge\`, but it
  is optional diagnostic material and not authority over project evidence.

## 4. Layer architecture

### Layer A - System Thinking / Jacque Fresco aligned layer

Target artifact:

```text
docs\semantic_dictionaries\system_thinking_dictionary_v1_ru.md
```

Purpose:

- environment -> behavior -> values -> system -> future design;
- system analysis;
- root cause reasoning;
- future design;
- project diagnosis.

First implementation:

- create the `docs\semantic_dictionaries\` directory if still missing;
- add one read-only reference artifact;
- include source status labels for every concept block;
- add a guard test only;
- do not connect the dictionary to runtime, planner, dispatch, Stage 4 builder,
  or Stage 4 adapter behavior.

### Layer B - Roger Saip concepts layer

Target artifacts may include:

```text
docs\semantic_dictionaries\roger_saip_concepts_v1_ru.md
docs\semantic_dictionaries\roger_saip_practical_models_v1_ru.md
```

Purpose:

- attention;
- mental control;
- reading and learning;
- memory;
- focus;
- weekly planning;
- saying no;
- purpose, vision, and action models.

First implementation:

- perform source evidence intake first;
- if safe source artifacts are absent, create no concept dictionary and report
  missing source evidence;
- if source artifacts are present, add read-only concept reference only;
- add a guard test for required headings, source labels, and boundaries;
- do not add productivity automation yet.

### Layer C - Ender's Game terminology layer

Target artifact:

```text
docs\semantic_dictionaries\enders_game_terminology_v1_ru.md
```

Purpose:

- training environment;
- simulation;
- command pressure;
- adversarial modeling;
- strategic empathy;
- feedback under stress;
- moral distance;
- victory condition;
- command responsibility.

First implementation:

- use summaries and project-safe concepts only;
- do not include copyrighted long quotes;
- format each entry as `term -> engineering meaning -> project use -> risk -> guard question`;
- mark source status explicitly;
- keep the artifact read-only reference only;
- add a guard test.

### Layer D - Semantic source index

Target artifact:

```text
docs\semantic_dictionaries\SEMANTIC_SOURCE_INDEX.md
```

Purpose:

- list all semantic dictionaries;
- record source status;
- record integration status;
- list guard tests;
- state allowed usage;
- state forbidden usage.

First implementation:

- include only dictionaries that exist or are explicitly planned;
- distinguish `present`, `missing source evidence`, `read-only reference`, and
  `not integrated`;
- do not make the index a runtime registry.

### Layer E - Semantic dictionary contract

Future target:

```text
contracts\semantic_dictionary_contract.v0.1.json
```

Purpose:

- define common structure for:
  - `id`;
  - `source_layer`;
  - `term`;
  - `definition`;
  - `project_use`;
  - `risk`;
  - `guard_question`;
  - `allowed_use`;
  - `forbidden_use`;
  - `status`.

This contract is not runtime-enforced until separately approved.

### Layer F - Semantic dictionary loader/validator

Future target:

```text
tools\semantic_dictionary_validator.py
```

Purpose:

- read-only loading;
- read-only validation;
- no runtime decisions;
- no external calls;
- no source project reads.

### Layer G - Semantic status CLI

Future target:

```text
tools\semantic_layers_status.py
```

Purpose:

- print dictionary inventory;
- print guard status;
- print source status;
- make no external calls;
- read no source projects;
- write no files.

### Layer H - Optional Stage 4 diagnostic annotation

Future target only after approval:

- optionally attach semantic diagnostics to a dry-run preview-handoff envelope;
- do not select actions;
- do not execute;
- do not grant planner decision authority;
- do not mutate runtime, storage, memory, ledger, session, workspace, lineage,
  or databases.

## 5. Implementation order

Use one bounded Codex slice per layer:

1. `32_ADD_SYSTEM_THINKING_DICTIONARY_REFERENCE`
2. `33_ADD_ROGER_SAIP_CONCEPTS_REFERENCE`
3. `34_ADD_ROGER_SAIP_PRACTICAL_MODELS_REFERENCE` if separate source evidence exists
4. `35_ADD_ENDERS_GAME_TERMINOLOGY_REFERENCE`
5. `36_ADD_SEMANTIC_SOURCE_INDEX`
6. `37_ADD_SEMANTIC_DICTIONARY_CONTRACT_DRAFT`
7. `38_ADD_SEMANTIC_DICTIONARY_LOADER_VALIDATOR`
8. `39_ADD_SEMANTIC_LAYERS_STATUS_CLI`
9. Later only with explicit approval: semantic diagnostics in Stage 4 dry-run
   envelope.

Prompt numbering currently matches the requested next prompt number sequence.
If a future prompt folder has already advanced beyond these numbers, keep the
next prompt number consistent with `D:\Codex_Prompts\GPTMEAi-SEMASCRIPT`.

## 6. Guard test strategy

Each read-only dictionary layer should add one focused `unittest` guard test.

For each dictionary artifact, test:

- file exists;
- file is UTF-8 readable;
- required headings exist;
- status says read-only/reference;
- source status is present;
- boundaries are present;
- forbidden usage is present;
- no wording implies runtime/API/planner implementation;
- no external dependency requirement appears.

Suggested first guard test target:

```text
tests\test_semantic_dictionaries_guard.py
```

Suggested checks for `system_thinking_dictionary_v1_ru.md`:

```python
required = (
    "# System Thinking Dictionary v1 RU",
    "Status: read-only reference",
    "Source status:",
    "Allowed use:",
    "Forbidden use:",
    "Guard questions:",
)
```

Future index tests should verify:

- `SEMANTIC_SOURCE_INDEX.md` exists;
- each listed dictionary path exists or is explicitly marked `missing source evidence`;
- each listed dictionary has an integration status;
- no entry is marked runtime-integrated without an approved implementation report.

Future contract tests should verify:

- `contracts\semantic_dictionary_contract.v0.1.json` is valid JSON;
- required fields are present;
- status remains draft/design-only;
- no runtime enforcement flag is enabled.

Future loader/validator tests should verify:

- only repository-local semantic dictionary files are loaded;
- invalid dictionary structure produces clear validation errors;
- no network, runtime, source project, or write primitives exist in the source.

Future status CLI tests should verify:

- `python -B tools\semantic_layers_status.py` exits `0`;
- output includes dictionary count, source status, integration status, and guard
  status;
- no watched project files change during the focused CLI run.

## 7. Verification commands

Use this standard verification set for semantic dictionary implementation
slices, adjusting `<new_test_files>` and `<new_test_module>` to the current
slice:

```powershell
python -B -m py_compile <new_test_files>
python -B -m unittest <new_test_module>
python -B tools\stage4_preview_handoff_status.py
python -B -m unittest tests.test_stage4_preview_handoff_status_cli
python -B -m unittest discover -s tests
python -B tools\run_local_verification.py
python -B tools\check_root_cleanliness.py
```

For this planning slice, the approved verification set is:

```powershell
python -B tools\stage4_preview_handoff_status.py
python -B -m unittest tests.test_stage4_preview_handoff_status_cli
python -B -m unittest discover -s tests
python -B tools\run_local_verification.py
python -B tools\check_root_cleanliness.py
```

## 8. Risk controls

Copyright risk:

- use summaries, concepts, and project-safe term mappings;
- do not include long copyrighted passages;
- do not present unverified excerpts as exact quotes.

Source evidence risk:

- if source files are absent, stop and request or define source intake;
- mark missing source evidence explicitly;
- do not invent dictionary entries from memory.

Semantic overreach:

- dictionaries are not authority over current files, logs, tests, contracts, or
  command output;
- dictionaries cannot override `AGENTS.md`;
- dictionaries cannot justify broader implementation.

Runtime leakage:

- semantic artifacts must not trigger execution or decisions;
- no loader, status CLI, or future diagnostic layer may call GPTMEAi runtime,
  SEMASCRIPT runtime, planner dispatch, or mutation endpoints.

Scope creep:

- implement one layer per Codex slice;
- keep every slice read-only until a separate approved contract or loader step.

Report discipline:

- every substantial slice creates one external
  `CHATGPT_REVIEW_REPORT.md` under `D:\Codex_Review_Reports\GPTMEAi-SEMASCRIPT`;
- report expected `tools\run_local_verification.py` refreshes separately from
  intentional edits.

## 9. Definition of Done for the plan

This planning slice is done when:

- this docs plan exists;
- all layers and implementation order are listed;
- boundaries and non-goals are stated;
- source evidence rules are stated;
- missing source evidence is recorded;
- guard test strategy is defined;
- verification commands are defined;
- full test/local verification remains green;
- no runtime, source project, API, planner, dispatch, contract, schema, code, or
  test changes occurred.

## 10. Recommended next bounded slice

Implement `32_ADD_SYSTEM_THINKING_DICTIONARY_REFERENCE` if it has not already
been completed; otherwise implement `33_ADD_ROGER_SAIP_CONCEPTS_REFERENCE`
after confirming source evidence availability.

Current evidence shows `docs\semantic_dictionaries\system_thinking_dictionary_v1_ru.md`
does not exist, so the next safest slice is:

```text
32_ADD_SYSTEM_THINKING_DICTIONARY_REFERENCE
```
