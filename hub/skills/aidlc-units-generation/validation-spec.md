# Validation Spec — aidlc-units-generation

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `[x] Workflow Planning`
- [ ] `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED` in `aidlc-docs/audit.md`
- [ ] Execute-IF criteria evaluated (skip if single simple unit, no decomposition needed)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/construction/{unit-name}/INDEX.md` (one per unit) | yes (if executed) | Each INDEX.md must contain: `**Unit**:`, `**Description**:`, `**AI Coverage**:`, `**Human Intervention Required**:`, `**Relates-To-ADR**:` (may be "N/A"), `## Scope`, `## Dependencies`, `## Construction Progress` checklist |
| `aidlc-docs/inception/plans/unit-of-work.md` | yes (if executed) | Master list of all units with IDs, descriptions, dependencies, and AI coverage |
| `aidlc-docs/inception/plans/unit-dependency-graph.md` | yes (if executed) | Mermaid dependency diagram (syntax validated per content-validation.md before writing) |
| `aidlc-docs/audit.md` | yes (append) | Must contain Part 1 decomposition plan presentation, raw user approval, Part 2 artifact generation completion, and `APPROVAL-STAGE: UNITS_GENERATION_APPROVED` |

**Skip artefact**: If skipped, `aidlc-docs/audit.md` must contain `SKIP: Units Generation — [rationale]` and `[x] Units Generation` is marked in state.md.

## Gate marker contract

This skill has **two approval gates** (Part 1 decomposition plan + Part 2 artifact generation), but only the final gate emits an audit marker.

**Part 1 gate** (decomposition plan approval):
- Pre-marker required: none within this skill (Part 1 is the first gate)
- No audit marker emitted at Part 1 — this is a wait-state only. Raw user approval is logged to audit.md.
- Log message: `APPROVAL-STAGE: UNITS_GENERATION_PLAN_APPROVED` is NOT written; only raw input logged.

**Part 2 gate** (artifact generation approval):
- Pre-marker required: Part 1 approval (wait-state — raw input logged to audit.md)
- Emit on Part 2 approval: `APPROVAL-STAGE: UNITS_GENERATION_APPROVED`
- No `[unit=...]` suffix (not a per-unit stage)
- `[x] Units Generation` is marked in `aidlc-docs/aidlc-state.md` on Part 2 approval

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| `[x] Workflow Planning` not present | Delegate to `aidlc-workflow`; return |
| Execute-IF not met (should skip) | Write `SKIP: Units Generation — [rationale]`; mark `[x]`; return |
| Mermaid dependency graph syntax invalid | Fix syntax before writing file; do NOT write invalid content |
| Unit INDEX.md missing `**Relates-To-ADR**:` field | Add field (may be "N/A") before presenting Part 2 gate |
| User selects "Request Changes" at Part 1 gate | Revise decomposition plan and re-present Part 1 gate (do NOT advance to Part 2) |
| User selects "Request Changes" at Part 2 gate | Revise unit INDEX files and re-present Part 2 gate (do NOT advance) |
