---
name: aidlc-reverse-engineering
description: >-
  Generate AI-DLC reverse-engineering artifacts for a brownfield project.
  Use when workspace detection reported brownfield and no reverse-engineering
  artifacts exist in aidlc-docs/inception/reverse-engineering/. Produces
  architecture docs, component inventory, API docs, and interaction diagrams.
allowed-tools: [Read, Edit, Write, Bash, Task]
phase: inception
stage: reverse-engineering
per-unit: false
human-clarification: required
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# AI-DLC Reverse Engineering

**Stage**: Inception — Reverse Engineering (CONDITIONAL — Brownfield only)
**Gate**: Explicit user approval before proceeding

## Prerequisite check (Step 0)

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

Read `references/state-contract.md`. Verify:
- `aidlc-docs/aidlc-state.md` exists and `Workspace State.Existing Code = Yes`
- `aidlc-docs/inception/reverse-engineering/` is absent or empty

If prerequisites not met -> delegate back to `aidlc-workflow` via Task tool and return.

## Step 1: Log start

Append to `aidlc-docs/audit.md` (use references/audit-format.md format).

## Step 2: Load full stage rules

Read `hub/inception/reverse-engineering.md` for detailed execution steps.

## Step 3: Execute reverse engineering

Follow all steps from the loaded `reverse-engineering.md` file:
- Analyze all packages and components
- Generate business overview covering business transactions
- Generate architecture documentation (C4 context + container diagrams)
- Generate code structure documentation
- Generate API documentation (endpoints, contracts)
- Generate component inventory
- Generate interaction diagrams (business transactions across components)
- Generate technology stack documentation
- Generate dependencies documentation

Output artifacts to `aidlc-docs/inception/reverse-engineering/`:
- `business-overview.md`
- `architecture.md`
- `code-structure.md`
- `api-docs.md`
- `component-inventory.md`
- `interaction-diagrams.md`
- `tech-stack.md`
- `dependencies.md`

## Step 4: Request advisory research (optional)

If unfamiliar tech stack encountered: use `aidlc-researcher` subagent via Task tool.

## Step 5: Approval gate

Present completion message (per `reverse-engineering.md` format):

```
## Reverse Engineering Complete

Generated artifacts:
- [list of files created]

**Options**:
A. Continue to Requirements Analysis
B. Request Changes to Reverse Engineering

[Answer]: _
```

Wait for user response. Log to audit.md (raw input). DO NOT PROCEED until approved.

## Step 6: On approval

Mark `[x] Reverse Engineering` in `aidlc-docs/aidlc-state.md`.
Log `APPROVAL-STAGE: REVERSE_ENGINEERING_APPROVED` to audit.md.
Notify user to continue with `aidlc-requirements-analysis` (or invoke `aidlc-workflow`).

