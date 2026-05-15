---
name: aidlc-workflow-planning
description: >-
  Plan which AI-DLC stages to execute and at what depth. Use after Requirements
  Analysis (and User Stories if executed) to determine the construction workflow
  before any per-unit work begins. Produces a Mermaid workflow diagram.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC Workflow Planning

**Stage**: Inception — Workflow Planning (ALWAYS EXECUTE)
**Gate**: Explicit user approval before proceeding

## Prerequisite check (Step 0)

Verify Requirements Analysis `[x]` in state. If not -> delegate to `aidlc-workflow`.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/inception/workflow-planning.md`.
Read `references/content-validation.md` — MANDATORY before any diagram creation.

## Step 2: Load all prior context

- Reverse engineering artifacts (if brownfield)
- `aidlc-docs/inception/requirements/requirements.md`
- User stories (if executed)
- `aidlc-docs/aidlc-state.md` — Extension Configuration

## Step 3: Determine stages and depth

For each stage, decide:
- Execute or Skip (with rationale)
- Depth: Minimal / Standard / Comprehensive
- Sequence and dependencies

## Step 4: Generate workflow plan document

Output `aidlc-docs/inception/plans/workflow-plan.md` with:
- Stage execution decision table
- Depth assignments
- Mermaid workflow diagram (VALIDATE syntax per content-validation.md before writing)
- Multi-package change sequence (if brownfield)

## Step 5: Validate content

Per `references/content-validation.md`:
- Validate Mermaid syntax
- Validate ASCII diagrams
- Check special character escaping

## Step 6: Approval gate

```
## Workflow Planning Complete

[Stage execution table and diagram]

User can override any stage inclusion/exclusion decision.

**Options**:
A. Approve workflow plan and proceed to Application Design / Construction
B. Request changes to workflow plan

[Answer]: _
```
Log raw input. DO NOT PROCEED until approved.

## Step 7: On approval

Mark `[x] Workflow Planning` in state.md.
Log `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED` to audit.md.
