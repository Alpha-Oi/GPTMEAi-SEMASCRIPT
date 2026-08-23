# GPTMAIOS Sci-Fi V4 Usage Guard Checklist

## Purpose

- GPTMAIOS Sci-Fi Engineering Terminology V4 is optional and diagnostic only.
- V4 is not a source of truth.
- Use V4 only when it improves an engineering check, risk note, constraint, test, rollback item, or next bounded slice.

## Priority Rule

Use this priority before applying any V4 terminology:

1. Current user prompt.
2. `AGENTS.md` / project contract.
3. Current files, logs, tests, and command output.
4. Source of Truth.
5. Evidence / Inference / Hypothesis discipline.
6. DCTP / 10D / Definition of Done / rollback safety.
7. V4 only after these as an additive diagnostic filter.

## Required Usage Formula

```text
Term -> engineering meaning -> check -> safe action
```

## Minimum Acceptance Criteria

Any report that claims V4 was used must show:

- at least one V4 term is named;
- why the term is relevant;
- a concrete check was performed or recommended;
- a concrete safe action, constraint, test, risk note, rollback item, or next bounded slice was produced;
- V4 is not presented as authority above project evidence.

## Anti-Patterns

Do not use V4 for:

- decorative analogy;
- justifying unapproved implementation;
- replacing file, log, test, or command-output inspection;
- expanding scope because a term suggests a larger architecture;
- making V4 mandatory for simple tasks.

## Report Snippet

```markdown
## V4 terminology filters used

- Term:
- Why relevant:
- Check performed:
- Action taken:
- Verification:
```

## Final Guard Question

```text
Did this V4 term produce a check or action?
If no, remove it.
```
