# Validation Spec — aidlc-functional-design

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists and contains an active unit entry
- [ ] Active unit `aidlc-docs/construction/{unit}/INDEX.md` exists
- [ ] Execute-IF criteria evaluated (skip if no new business logic or simple implementation changes)
- [ ] No prior `APPROVAL-STAGE` required for the first Construction stage of a unit (or prior stage was skipped)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/construction/{unit}/functional-design/` (directory) | yes (if executed) | Must contain: data models and schemas (SID GB922 alignment if applicable), business rules and validation logic, domain events and commands, error scenarios and edge cases, hexagonal architecture layer mapping |
| `aidlc-docs/construction/{unit}/INDEX.md` | yes (update) | Must have `**Relates-To-ADR**:` field with ADR number(s) or "N/A" |
| `aidlc-docs/audit.md` | yes (append) | Must contain start log entry and `APPROVAL-STAGE: FUNCTIONAL_DESIGN_APPROVED [unit={unit}]` on completion |

**Conditional artefact**:
- If vague-keyword scan finds `depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`: create `aidlc-docs/construction/{unit}/functional-design-questions.md` (per question-format-guide.md). All `[Answer]:` tags must be filled and incorporated before approval gate.

**Skip artefact**: If skipped, `aidlc-docs/audit.md` must contain `SKIP: Functional Design — {unit} — [rationale]` and `[x] Functional Design` is marked in unit's construction progress.

## Gate marker contract

- Expected pre-marker: none required for first Construction stage (or `SKIP: ...` for skipped prior stages)
- Emit on completion: `APPROVAL-STAGE: FUNCTIONAL_DESIGN_APPROVED [unit={unit}]`
- Marker is appended to `aidlc-docs/audit.md`
- `[x] Functional Design` is marked in the unit's `## Construction Progress` in `aidlc-docs/construction/{unit}/INDEX.md`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: `adr-curator` — if a new architecturally significant decision surfaces during Step 2 (ADR consultation). Must complete BEFORE approval gate is presented.

## Failure modes

| Condition | Action |
|---|---|
| Active unit not identified in state | Delegate to `aidlc-workflow`; return |
| Execute-IF not met (should skip) | Write skip entry; mark `[x] Functional Design`; return |
| No existing ADR governs a significant design decision | Invoke `adr-curator`; wait for ADR draft; cite in output before gate |
| `**Relates-To-ADR**:` field missing from INDEX.md | Add field (may be "N/A") before presenting gate — BLOCKING |
| Vague-keyword scan finds issues | Create questions file; wait for all answers; update artifact before gate |
| User selects "Option 1 — Request Changes" at gate | Update artifact; re-present the same gate (do NOT advance) |
