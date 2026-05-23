# Validation Spec — aidlc-application-design

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `[x] Workflow Planning`
- [ ] `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED` in `aidlc-docs/audit.md`
- [ ] Execute-IF criteria evaluated (skip if changes within existing component boundaries and no new components/methods)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/inception/application-design/` (directory) | yes (if executed) | Must contain: component inventory (new components), service layer definition (ports, adapters), component interactions and dependencies, business rules per component, integration points with existing components |
| `aidlc-docs/audit.md` | yes (append) | Must contain start log entry and `APPROVAL-STAGE: APPLICATION_DESIGN_APPROVED` on completion |

**ADR backlink requirement**: Any architectural decision made during this stage must be cited with an ADR number in the output documents. If no existing ADR governs the decision, `adr-curator` must be invoked first.

**Skip artefact**: If skipped, `aidlc-docs/audit.md` must contain `SKIP: Application Design — [rationale]` and `[x] Application Design` is marked in state.md.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED`
- Emit on completion: `APPROVAL-STAGE: APPLICATION_DESIGN_APPROVED`
- Marker is appended to `aidlc-docs/audit.md` (no `[unit=...]` suffix)
- `[x] Application Design` is marked in `aidlc-docs/aidlc-state.md`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**:
  - `aidlc-researcher` — if unfamiliar tech stack or patterns involved (Step 4). Advisory, not blocking the approval gate.
  - `adr-curator` — if a significant architectural decision has no existing ADR (Step 6). Must complete BEFORE approval gate is presented.

## Failure modes

| Condition | Action |
|---|---|
| `[x] Workflow Planning` not present | Delegate to `aidlc-workflow`; return |
| Execute-IF not met (should skip) | Write `SKIP: Application Design — [rationale]`; mark `[x]`; return |
| Significant architectural decision has no ADR | Invoke `adr-curator`; wait for ADR draft; cite ADR number in design output before presenting gate |
| User selects "Request Changes" at gate | Revise design output and re-present gate (do NOT advance) |
