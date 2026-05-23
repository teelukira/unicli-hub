# Validation Spec — aidlc-operations

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists
- [ ] All Construction units have `[x] Build and Test` in their progress
- [ ] `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={last-unit}]` in `aidlc-docs/audit.md` for all units

## Artefact contract

This stage is a **placeholder** — it produces no real artefacts.

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/audit.md` | yes (append) | Must contain `## Operations Phase` log entry with ISO 8601 timestamp, user request, and AI response confirming placeholder display |

There are no output documents, design artefacts, or code artefacts for this stage in its current placeholder state.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={last-unit}]` for all completed units
- **No `APPROVAL-STAGE` marker is emitted.** This placeholder stage has no approval gate (per SKILL.md: "Gate: None").
- Completion is recorded only as a log entry in `aidlc-docs/audit.md`.

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| Not all Construction units complete | N/A — coordinator (`aidlc-workflow`) guards dispatch; this skill assumes all units are done |
| Invoked without completing all units | Log to audit.md; display placeholder message; note which units are incomplete |
