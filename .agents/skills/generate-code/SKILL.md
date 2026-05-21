---
name: generate-code
description: >-
  Generate production-quality code for the active feature or task. Use when the user asks to implement, add, or write code.
allowed-tools: [Read, Edit, Write, Bash]
---

## When to Use

- Implementing a new feature, endpoint, or module.
- Adding or modifying a function, class, or component.
- Any change that requires corresponding tests.

## Prerequisites

Before writing any code, read:
- `{RULES_DIR}/common/codegen-principles.md` — coding principles (MANDATORY)
- `{RULES_DIR}/common/conventions.md` — project naming and style conventions
- `{ADR_INDEX}` — scan for ADRs governing the target area

## Steps

### 1. Understand the requirement

State the single behaviour to implement in one sentence.
Identify the layer / module affected.
Confirm no existing code already handles this.

### 2. ADR gate

Check `{ADR_INDEX}` for ADRs that cover the target area.
- `Accepted` ADR → follow without deviation.
- New architectural decision needed → STOP, invoke `adr-curator` first.

### 3. Red — Write the failing test first

Write a test that defines the expected behaviour.
Confirm it fails before writing implementation code.

```
// {LANGUAGE} example
{TEST_EXAMPLE_PLACEHOLDER}
```

### 4. Green — Minimal passing implementation

Write the simplest code that makes the test pass.
Follow layer boundaries defined in `{RULES_DIR}/common/architecture.md`.
Apply framework-specific rules from `{RULES_DIR}/common/tech-stack.md`.

### 5. Refactor

Separate structural changes from behavioural changes (Tidy First).
Re-run tests after every structural change.

### 6. Commit

All tests green before committing.
Commit message format: `{COMMIT_PREFIX}: <short description>`.

## Output

- List of created / modified files (relative paths).
- Test results summary.
- `Relates-To-ADR:` citation line.
- Any follow-up items marked `TODO(codegen):`.

## Guard

- Never commit code that fails to compile or has failing tests.
- Never skip the Red phase.
- Never put generated code in `{DOCS_DIR}`.

