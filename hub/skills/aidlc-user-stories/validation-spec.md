# Validation Spec — aidlc-user-stories

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `[x] Requirements Analysis`
- [ ] `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED` in `aidlc-docs/audit.md`
- [ ] Execute-IF criteria evaluated (skip if pure internal refactor / infrastructure-only / docs-only)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/inception/user-stories/` (directory) | yes (if executed) | Must contain persona profiles, user stories (As a / I want / So that format), acceptance criteria per story, and story map |
| `aidlc-docs/audit.md` | yes (append) | Must contain Part 1 plan presentation, raw user approval input, Part 2 generation completion, and `APPROVAL-STAGE: USER_STORIES_APPROVED` |

**Skip artefact**: If skipped, `aidlc-docs/audit.md` must contain `SKIP: User Stories — [rationale]` and `[x] User Stories` is marked in state.md.

## Gate marker contract

This skill has **two approval gates** (Part 1 plan + Part 2 generation), but only the final gate emits an audit marker.

**Part 1 gate** (plan approval):
- Pre-marker required: none within this skill (Part 1 is the first gate)
- No audit marker emitted at Part 1 — this is a wait-state only. Raw user approval is logged to audit.md.

**Part 2 gate** (generation approval):
- Pre-marker required: Part 1 approval (wait-state — raw input logged to audit.md)
- Emit on Part 2 approval: `APPROVAL-STAGE: USER_STORIES_APPROVED`
- No `[unit=...]` suffix (not a per-unit stage)
- `[x] User Stories` is marked in `aidlc-docs/aidlc-state.md` on Part 2 approval

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| `[x] Requirements Analysis` not present | Delegate to `aidlc-workflow`; return |
| Execute-IF not met (should skip) | Write `SKIP: User Stories — [rationale]`; mark `[x]`; return |
| User selects "Request Changes" at Part 1 gate | Revise story plan and re-present Part 1 gate (do NOT advance to Part 2) |
| User selects "Request Changes" at Part 2 gate | Revise generated stories and re-present Part 2 gate (do NOT advance) |
