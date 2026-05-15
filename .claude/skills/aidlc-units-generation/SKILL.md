---
name: aidlc-units-generation
description: >-
  Decompose AI-DLC scope into deployable units of work in two parts (plan
  then generate). Use when the system needs breakdown into multiple services
  or modules. Skip for single-unit or straightforward single-component work.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC Units Generation

**Stage**: Inception — Units Generation (CONDITIONAL)
**Gate**: Explicit user approval after Part 1 (decomposition plan) AND Part 2 (unit generation)

## Prerequisite check (Step 0)

Read `references/state-contract.md`. Verify Workflow Planning `[x]` in state.

Evaluate Execute-IF / Skip-IF:
- **Execute IF**: System decomposition into multiple units needed; multiple services/modules required; structured breakdown needed for complex system
- **Skip IF**: Single simple unit; no decomposition needed; straightforward single-component implementation

If skip: write `SKIP: Units Generation — [rationale]` to audit.md. Mark `[x]`. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/inception/units-generation.md`.

## Step 2: Load context

Read all prior inception artifacts (RE, requirements, user stories, workflow plan, app design).

## PART 1 — Decomposition Planning

## Step 3: Create decomposition plan

Generate:
- Proposed unit list with names and descriptions
- Unit dependencies and sequence
- AI coverage estimates per unit
- Human intervention points per unit (CRITICAL items requiring human review)
- Open questions before finalizing

## Step 4: Part 1 approval gate

```
## 🔵 Units Generation — Part 1: Decomposition Plan

[Unit list with dependencies]

**Options**:
A. Approve decomposition plan and generate unit artifacts
B. Request changes to unit plan

[Answer]: _
```
Log raw input. DO NOT proceed to Part 2 until approved.

## PART 2 — Unit Artifact Generation

## Step 5: Generate unit artifacts

For each approved unit, create `aidlc-docs/construction/{unit-name}/INDEX.md`:

```markdown
# {Unit Name} — Unit of Work

**Unit**: {unit-id}
**Description**: {description}
**AI Coverage**: {percentage}%
**Human Intervention Required**: {list critical human checks}
**Relates-To-ADR**: {ADR numbers or "N/A"}

## Scope

[What this unit implements]

## Dependencies

[Units that must complete before this one]

## Construction Progress

- [ ] Functional Design
- [ ] NFR Requirements
- [ ] NFR Design
- [ ] Infrastructure Design
- [ ] Code Generation
- [ ] Build and Test
```

Also create:
- `aidlc-docs/inception/plans/unit-of-work.md` (master list)
- `aidlc-docs/inception/plans/unit-dependency-graph.md` (Mermaid diagram — validate first)

## Step 6: Part 2 approval gate

```
## 🔵 Units Generation — Part 2: Artifacts Complete

[Summary of generated unit INDEX files]

**Options**:
A. Approve units and proceed to Construction
B. Request Changes to Units

[Answer]: _
```
Log raw input. Mark `[x] Units Generation` on approval.
Log `APPROVAL-STAGE: UNITS_GENERATION_APPROVED` to audit.md.
