---
name: generate-plan
description: >-
  Create an implementation plan before writing code. Use when the task is non-trivial or requires clarifying approach before coding.
allowed-tools: [Read, Bash]
---

## When to Use

- Before starting any change touching more than one file.
- At the start of a new unit of work (Code Generation Part 1).
- When scope or approach needs alignment before coding begins.

## Prerequisites

- Design documents for the active unit (functional, NFR, infrastructure).
- `{ADR_INDEX}` — scan for relevant ADRs.
- Active unit entry in `{STATE_FILE}`.

## Steps

### 1. Clarify intent

State the goal in one sentence. Ask one clarifying question if ambiguous.

> **Goal**: `{ONE_SENTENCE_GOAL}`

### 2. Scope assessment

Identify which layers and files are affected:

```
{LAYER_1}/    — new model, port, or service?
{LAYER_2}/    — new controller or DTO?
{LAYER_3}/    — new persistence, migration, or messaging?
{LAYER_4}/    — new config or integration test?
```

### 3. ADR gate

Scan `{ADR_INDEX}` for ADRs covering the target area.
- `Accepted` → cite in plan, follow without deviation.
- `Proposed` → flag as dependency; do not conflict.
- New decision needed → STOP, invoke `adr-curator`.

### 4. Extension check

Read `{STATE_FILE}` Extension Configuration.
Add tasks for each enabled extension (e.g. PBT tests, security controls).

### 5. Build the plan (checkbox format)

```markdown
## Implementation Plan — {UNIT_OR_FEATURE_NAME}

**Goal**: {ONE_SENTENCE_GOAL}
**Relates-To-ADR**: {ADR_NUMBERS}

### {LAYER_1} changes
- [ ] {FILE_PATH} — {what changes}
- [ ] {FILE_PATH} — {what changes}

### {LAYER_2} changes
- [ ] {FILE_PATH} — {what changes}

### Tests
- [ ] {TEST_FILE} — unit test (Red → Green → Refactor)
- [ ] {TEST_FILE} — integration / E2E test

### Verification
- [ ] {BUILD_COMMAND} — clean build
- [ ] {TEST_COMMAND} — all tests green
- [ ] {EXTRA_CHECK} — (linting, compliance, etc.)
```

### 6. Risks and dependencies

List any blockers, external dependencies, or known constraints.

### 7. Effort estimate

| Area | Files | Complexity | Est. |
|------|-------|-----------|------|
| {AREA} | {N} | Low / Med / High | {T} min |

### 8. Approval gate

```
## Plan — {FEATURE_NAME}

{full checkbox plan}

**STOP** — Do not proceed until the user explicitly approves.

---
**Option 1 — Request Changes**: Describe what needs to change.
**Option 2 — Continue to Code Generation**: Execute the plan.
```

Log the user's raw response to `{AUDIT_LOG}`.

## Output

- Checkbox plan saved to `{PLAN_OUTPUT_PATH}`.
- ADR citation line.
- Risk / dependency list.
- Effort estimate table.

## Guard

- Never start writing code before the plan is approved.
- Every implementation task must have a corresponding test task.
- Plan files go in `{DOCS_DIR}`, not in application code directories.

