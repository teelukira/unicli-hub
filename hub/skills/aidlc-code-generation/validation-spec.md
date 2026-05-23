# Validation Spec — aidlc-code-generation

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists and contains an active unit entry
- [ ] Active unit has Infrastructure Design stage status `done` or `skipped`
- [ ] `audit.md` tail contains `APPROVAL-STAGE: INFRASTRUCTURE_DESIGN_APPROVED [unit={unit}]` or `INFRASTRUCTURE_DESIGN_SKIPPED [unit={unit}]`
- [ ] `aidlc-docs/construction/{unit}/functional-design/` directory exists

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/construction/{unit}/code/code-generation-plan.md` | yes | Must contain checkboxes for at least one subagent section (Backend / Database / Frontend / IaC) |
| `aidlc-docs/construction/{unit}/INDEX.md` | yes | Must have `**Relates-To-ADR**:` field (may be "none") |

## Gate marker contract

**Part 1 gate** (plan approval):
- Pre-marker required: none (first gate in this skill)
- Emit on Part 1 approval: `APPROVAL-STAGE: CODE_GENERATION_PLAN_APPROVED [unit={unit}]`

**Part 2 gate** (execution approval):
- Pre-marker required: `APPROVAL-STAGE: CODE_GENERATION_PLAN_APPROVED [unit={unit}]`
- Emit on Part 2 approval: `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]`

Both markers are appended to `aidlc-docs/audit.md`.

## Subagent dispatch contract

**BLOCKING subagents** (all dispatched concurrently, all must complete before Part 2 gate):
- `codegen-backend` — if backend Java/Spring Boot code in plan
- `codegen-db` — if Flyway migrations or JPA entities in plan
- `codegen-frontend` — if React/TypeScript code in plan
- `codegen-iac` — if Terraform/infra code in plan

At least one BLOCKING subagent must be dispatched.

**Conditional subagents**:
- `adr-curator` — if a new architectural decision surfaces during Step 2 (ADR consultation). Dispatch BEFORE continuing to PART 1.

## Failure modes

| Condition | Action |
|---|---|
| Missing precondition (Infrastructure Design not done/skipped) | Halt; display current unit progress table; ask user to complete prior stage |
| Part 1 plan has no checkboxes for any subagent | Halt; regenerate plan with explicit subagent breakdown |
| All dispatched subagents fail | Halt; surface each subagent's error; request user intervention before Part 2 gate |
| User selects "Request Changes" at either gate | Revise and re-present the same gate (do NOT advance to next step) |
