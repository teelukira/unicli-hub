---
name: aidlc-user-stories
description: >-
  Generate AI-DLC user stories and personas in two parts (plan then generate).
  Use after Requirements Analysis when the change is user-facing, involves
  multiple personas, or requires acceptance criteria. Skip for pure internal
  refactors, infrastructure-only, or documentation-only changes.
allowed-tools: [Read, Edit, Write]
phase: inception
stage: user-stories
per-unit: false
human-clarification: required
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# AI-DLC User Stories

**Stage**: Inception — User Stories (CONDITIONAL)
**Gate**: Explicit user approval after Part 1 (plan) AND Part 2 (generation)

## Prerequisite check (Step 0)

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

Read `references/state-contract.md`. Verify:
- Requirements Analysis `[x]` in `aidlc-docs/aidlc-state.md`

Evaluate Execute-IF / Skip-IF (from `references/inception-conditions.md`):
- **Skip**: Write `SKIP: User Stories — [rationale]` to audit.md. Mark `[x]`. Return.
- **Execute**: Proceed.

## Step 1: Log start and load rules

Append to audit.md. Read `hub/inception/user-stories.md`.

## Step 2: Load context

Read `aidlc-docs/inception/requirements/requirements.md`.
Read reverse-engineering artifacts if brownfield.

## PART 1 — Story Planning

## Step 3: Create story plan

Generate a story plan with:
- Identified user personas
- Story categories
- Questions requiring answers before generation
- Acceptance criteria structure

Use `references/question-format.md` for any clarifying questions.

## Step 4: Part 1 approval gate

Present plan to user:
```
## User Stories — Part 1: Plan Complete

[Story plan with personas, categories, open questions]

**Options**:
A. Approve plan and proceed to story generation
B. Request changes to story plan

[Answer]: _
```
Log raw input. DO NOT proceed to Part 2 until approved.

## PART 2 — Story Generation

## Step 5: Generate stories

Execute approved plan to generate:
- Persona profiles
- User stories (As a... I want... So that...)
- Acceptance criteria per story
- Story map

Output: `aidlc-docs/inception/user-stories/`

## Step 6: Part 2 approval gate

```
## User Stories — Part 2: Generation Complete

[Summary of generated stories and personas]

**Options**:
A. Continue to Workflow Planning
B. Request Changes to User Stories

[Answer]: _
```
Log raw input. Mark `[x] User Stories` on approval.
Log `APPROVAL-STAGE: USER_STORIES_APPROVED` to audit.md.
