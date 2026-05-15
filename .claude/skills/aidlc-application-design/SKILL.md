---
name: aidlc-application-design
description: >-
  Run AI-DLC Application Design. Use when new components, services, methods,
  or component dependencies need definition for the current workstream. Skip
  when changes stay within existing component boundaries or are pure
  implementation changes with no new components.
allowed-tools: [Read, Edit, Write, Task]
---

# AI-DLC Application Design

**Stage**: Inception — Application Design (CONDITIONAL)
**Gate**: Explicit user approval before proceeding

## Prerequisite check (Step 0)

Read `references/state-contract.md`. Verify Workflow Planning `[x]` in state.

Evaluate Execute-IF / Skip-IF:
- **Execute IF**: New components/services needed; component methods/business rules need definition; service layer design required; component dependencies need clarification
- **Skip IF**: Changes within existing component boundaries; no new components/methods; pure implementation changes

If skip: write `SKIP: Application Design — [rationale]` to audit.md. Mark `[x]`. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/inception/application-design.md`.

## Step 2: Load context

Read reverse-engineering artifacts (if brownfield).
Read `aidlc-docs/inception/requirements/requirements.md`.
Read `aidlc-docs/inception/user-stories/` (if exists).

## Step 3: Determine depth

Minimal / Standard / Comprehensive per `common/depth-levels.md`.

## Step 4: Advisory research (if needed)

If unfamiliar tech stack or patterns involved:
Invoke `aidlc-researcher` subagent via Task tool (advisory, not BLOCKING):
```
Task({
  description: "Research [tech/pattern] for application design",
  prompt: "Research [specific technology or pattern] for [context]. Output to aidlc-docs/research/. Provide summary of findings.",
  subagent_type: "aidlc-researcher"
})
```

## Step 5: Execute application design

Per loaded `application-design.md` steps:
- Define component inventory (new components)
- Define service layer (ports, adapters)
- Define component interactions and dependencies
- Define business rules per component
- Identify integration points with existing components

Output: `aidlc-docs/inception/application-design/`

## Step 6: ADR check

For any significant architectural decision made:
- Scan `aidlc-docs/index/adr-index.md` for existing ADR
- If none: invoke `adr-curator` to draft a new ADR
- Cite ADR number in application design output

## Step 7: Approval gate

```
## 🔵 Application Design Complete

[Component diagram and description]

**Options**:
A. Continue to Units Generation / Construction
B. Request Changes to Application Design

[Answer]: _
```
Log raw input. DO NOT PROCEED until approved.

## Step 8: On approval

Mark `[x] Application Design` in state.md.
Log `APPROVAL-STAGE: APPLICATION_DESIGN_APPROVED` to audit.md.
