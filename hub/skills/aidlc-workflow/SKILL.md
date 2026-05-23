---
# COORDINATOR: do not invoke as a stage skill
name: aidlc-workflow
description: >-
  AI-DLC workflow coordinator. Use FIRST whenever the user requests software
  development, says "start AI-DLC", "continue AI-DLC", "resume my project",
  "what's next in AI-DLC", "advance the workflow", or asks to start/continue
  any AI-DLC stage. Reads aidlc-docs/aidlc-state.md and dispatches to the
  correct aidlc-<stage> skill.
allowed-tools: [Read, Task]
phase: coordinator
stage: workflow
per-unit: false
human-clarification: none
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# AI-DLC Workflow Coordinator

**Role**: Thin state-machine coordinator. Read state → pick next skill → delegate via Task tool.
Do NOT perform stage work directly. All stage execution happens inside the dispatched skill.

## Step 0: Load references

Before any decision, read these reference files:
- `references/welcome-message.md` — welcome banner (display once per session at cold start)
- `references/session-continuity.md` — resume template

## Step 1: Check state file

Read `aidlc-docs/aidlc-state.md` — header sections ONLY:
- `## Project Information`
- `## AI-DLC Active Workstream`
- `## Workspace State`
- `## Extension Configuration`

If file does not exist (first-ever run):
1. Display `references/welcome-message.md` banner
2. Dispatch → `aidlc-workspace-detection` via Task tool
3. Return (do not continue coordinator logic)

## Step 2: Session continuity

If this is the first assistant turn in the session:
- Display "Welcome back" prompt from `references/session-continuity.md`
- Show current stage and active unit
- If Construction >= Code Generation stage: mention MANDATORY Jira Reconciliation
- Ask user: Continue or Review prior stage?
- Wait for response before dispatching

## Step 3: Parse state

Extract from state file:
```
project_type    <- state.ProjectType (greenfield | brownfield)
active_unit     <- state.ActiveWorkstream.unit (e.g., "U24" or null)
ext_config      <- state.ExtensionConfiguration table
last_marker     <- last APPROVAL-STAGE or GATE-* line in aidlc-docs/audit.md (tail only)
```

## Step 4: Approval gate guard

**CRITICAL**: Read `common/gate-protocol.md`. Enforce the following before dispatching any Construction skill.

### 4a. Check for prior stage APPROVAL or SKIP marker

Scan the **last 40 lines** of `aidlc-docs/audit.md` for the prior stage's marker:
- Valid approval: `APPROVAL-STAGE: {PREV_STAGE}_APPROVED [unit={unit}]`
- Valid skip: `SKIP: {stage name} — {unit} — ...`

If **neither** found:
1. Re-display the 2-option gate message for the prior stage (from its SKILL.md Step format)
2. Wait for user response
3. Log response to audit.md
4. Re-enter Step 3

Do NOT dispatch the next stage until a valid marker exists.

### 4b. Marker format correction

If `{PREV_STAGE}_COMPLETE` (wrong suffix) is found but no `_APPROVED`:
- Inform user: "마커 형식 드리프트 발견 (`_COMPLETE` → `_APPROVED`). 이전 단계를 승인 처리하고 계속할까요?"
- On yes: write corrected `APPROVAL-STAGE: {PREV_STAGE}_APPROVED [unit={unit}]` to audit.md, proceed
- On no: treat as pending gate — wait

### 4c. Hard blockers (never bypass)

| Dispatch target | Required prior marker |
|---|---|
| Code Generation Part 2 (codegen subagents) | `CODE_GENERATION_PLAN_APPROVED` |
| Build and Test | `CODE_GENERATION_APPROVED` |
| Next unit / Operations | `BUILD_AND_TEST_APPROVED` |

If the required marker is absent: block dispatch, re-display the relevant gate, wait.

## Step 5: Inception decision tree

Execute only if Inception is not fully complete (check stage checkboxes):

```
[ ] Workspace Detection  -> dispatch aidlc-workspace-detection
[ ] Reverse Engineering  -> dispatch aidlc-reverse-engineering  (IF brownfield AND no RE artifacts)
[ ] Requirements Analysis -> dispatch aidlc-requirements-analysis
[ ] User Stories         -> dispatch aidlc-user-stories         (IF Execute-IF criteria met)
[ ] Workflow Planning    -> dispatch aidlc-workflow-planning
[ ] Application Design   -> dispatch aidlc-application-design   (IF Execute-IF criteria met)
[ ] Units Generation     -> dispatch aidlc-units-generation      (IF Execute-IF criteria met)
```

For CONDITIONAL stages: evaluate Execute-IF / Skip-IF criteria from `references/inception-conditions.md`.
When skipping: write `SKIP: <stage> — <rationale>` to audit.md, mark checkbox `[x]`.

## Step 6: Construction per-unit loop

When Inception is complete, execute the per-unit loop:

For `active_unit` (or next pending unit from units-of-work list):
```
[ ] Functional Design     -> dispatch aidlc-functional-design     (IF Execute-IF)
[ ] NFR Requirements      -> dispatch aidlc-nfr-requirements      (IF Execute-IF)
[ ] NFR Design            -> dispatch aidlc-nfr-design            (IF nfrR complete)
[ ] Infrastructure Design -> dispatch aidlc-infrastructure-design  (IF Execute-IF)
[ ] Code Generation       -> dispatch aidlc-code-generation       (ALWAYS)
[ ] Build and Test        -> dispatch aidlc-build-and-test        (ALWAYS, after CG complete)
```

When all unit checkboxes are `[x]` AND `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED` is in audit.md:
- Mark unit complete in state
- Advance to next unit OR dispatch `aidlc-operations`

## Step 7: Operations

When all Construction units are complete -> dispatch `aidlc-operations`.

## Extension awareness

Before dispatching any Construction skill, check `ext_config`:
- If `ADR Governance: Enabled (Full)` -> remind dispatched skill to enforce ADR gates
- If `TMF Compliance: Enabled (Full)` -> build-and-test will enforce GATE-TMF
- If `Security Baseline: Disabled` -> skip security gate enforcement
- If `Property-Based Testing: Enabled (Full)` -> code-generation enforces PBT

The coordinator only reads ext_config — it NEVER writes it. Only `aidlc-requirements-analysis` writes it.

## Dispatch pattern (Task tool)

```
Task({
  description: "Run aidlc-<stage> skill for [active_unit / context]",
  prompt: "You are the aidlc-<stage> skill. [Stage-specific context from state]. [relevant ext_config flags]. Proceed.",
  subagent_type: "aidlc-<stage>"
})
```

Always include in the Task prompt:
1. Active unit name and description
2. Relevant extension flags
3. Any pending user answer from session-continuity step
