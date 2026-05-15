---
name: aidlc-code-generation
description: >-
  Run per-unit AI-DLC Code Generation in two parts (plan then execute). Use
  when the active construction unit has completed design stages and is ready
  for code generation. Dispatches to codegen-backend, codegen-frontend,
  codegen-db, or codegen-iac subagents as BLOCKING gates.
allowed-tools: [Read, Edit, Write, Bash, Task]
---

# AI-DLC Code Generation

**Stage**: Construction — Code Generation (ALWAYS EXECUTE per unit)
**Gate**: Standardized 2-option approval after Part 1 (plan) AND Part 2 (generation)
**HITL Gate Reference**: `.unicli-rules/common/gate-protocol.md`

## Prerequisite check (Step 0)

Read `references/state-contract.md`. Identify active unit.
Verify: Infrastructure Design done (or skipped) in unit progress.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/construction/code-generation.md`.
Read `references/codegen-principles.md` — MANDATORY before any code plan.
Read `references/jira-integration.md` — MANDATORY before Jira ticket creation.

## Step 2: ADR consultation

Read `aidlc-docs/index/adr-index.md`. Any ADR governing this unit's tech decisions must be cited in the code plan. If a new architectural decision surfaces: invoke `adr-curator` via Task tool before continuing.

## Step 3: Check extension enforcement

Read `aidlc-docs/aidlc-state.md` Extension Configuration:
- `Property-Based Testing: Enabled (Full)` → jqwik PBT required in code plan
- `ADR Governance: Enabled (Full)` → ADR backlinks required
- `Security Baseline: Enabled (Full)` → security controls required

## PART 1 — Planning

## Step 4: Create code generation plan

Generate a detailed plan with checkboxes for every file to be created. Format:

```
## Code Generation Plan — {Unit Name}

### Backend (codegen-backend)
- [ ] domain/src/…/port/…Port.java
- [ ] domain/src/…/service/…Service.java
- [ ] api/src/…/controller/…Controller.java
…

### Database (codegen-db)
- [ ] app/src/main/resources/db/migration/V{n}__create_{table}.sql
- [ ] infrastructure/src/…/entity/…Entity.java
…

### Frontend (codegen-frontend) — if applicable
- [ ] frontend/src/pages/…
…

### Tests
- [ ] domain/src/test/… (unit tests — TDD Red→Green→Refactor)
- [ ] api/src/test/… (integration tests with Testcontainers/REST Assured)
…
```

## Step 5: Part 1 approval gate

```
## Code Generation — Part 1: Plan Complete — {Unit Name}

**Artifact(s)**:
- `aidlc-docs/construction/{unit}/code/code-generation-plan.md`

{Full code generation plan with checkboxes}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change in the plan.
**Option 2 — Continue to Code Generation**: Proceed to execute the plan.
```

Log raw input. DO NOT execute until plan approved.
On "Continue": log `APPROVAL-STAGE: CODE_GENERATION_PLAN_APPROVED [unit={unit}]` to audit.md before dispatching any codegen subagent.

## PART 2 — Code Generation Execution

## Step 6: Jira In Progress transition (MANDATORY)

Tickets were created at Requirements Analysis. Now transition them:
1. Read `common/jira-integration.md` §3. Read unit's `**Jira Ticket**` entries from `aidlc-docs/aidlc-state.md`.
2. Transition each ticket to In Progress (`transition_id_inprogress: "21"`).
3. Log `JIRA-INPROGRESS: NWAE-### [unit=Uxx]` to audit.md for each ticket.

On failure: log per §4 of jira-integration.md — do NOT block code generation.

## Step 7: Dispatch codegen subagents (BLOCKING)

Determine which codegen subagents to invoke based on unit scope.

**Backend** (if backend code in plan):
```
Task({
  description: "Generate backend code for {unit}",
  prompt: "You are the codegen-backend agent. Generate all backend Java/Spring Boot code for unit {unit-name}. Follow TDD Red→Green→Refactor. Use hexagonal architecture (domain/api/infrastructure/app). Enforce property-based testing if PBT extension Enabled. ADR references: {list}. Code plan: {plan excerpt}. Codegen principles: apply Karpathy P1-P4 + Kent Beck TDD. Output code to workspace root {service-name}/.",
  subagent_type: "codegen-backend"
})
```

**Database** (if DB migrations in plan):
```
Task({
  description: "Generate DB migrations for {unit}",
  prompt: "You are the codegen-db agent. Generate Flyway migrations and JPA entities for unit {unit-name}. Follow SID GB922 naming. Migration prefix: V{n}__. Output to {service-name}/app/src/main/resources/db/migration/.",
  subagent_type: "codegen-db"
})
```

**Frontend** (if frontend code in plan):
```
Task({
  description: "Generate frontend code for {unit}",
  prompt: "You are the codegen-frontend agent. Generate React 18 + TypeScript code for unit {unit-name}. Use TanStack Router/Query. Follow ATOM Design System. Generate Playwright E2E tests. Output to frontend/src/.",
  subagent_type: "codegen-frontend"
})
```

**IaC** (if infra code in plan):
```
Task({
  description: "Generate Terraform IaC for {unit}",
  prompt: "You are the codegen-iac agent. Generate Terraform for {unit}. Follow existing infra/ patterns. Output to infra/.",
  subagent_type: "codegen-iac"
})
```

Wait for ALL dispatched subagents to complete (BLOCKING).

## Step 8: Mark plan checkboxes

As each subagent completes, mark the corresponding plan checkboxes `[x]`.
Update plan in `aidlc-docs/construction/{unit}/code/code-generation-plan.md`.

## Step 9: Update INDEX backlink

Update `aidlc-docs/construction/{unit}/INDEX.md` — ensure `**Relates-To-ADR**:` is present and up-to-date.

## Step 10: Part 2 approval gate

```
## Code Generation — Part 2: Complete — {Unit Name}

**Generated files**: {count} files across {subagent list}

{Summary of generated files by subagent}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe issues found. I will fix and re-present this gate.
**Option 2 — Continue to Build and Test**: Proceed to QA verification.
```

Log raw input. DO NOT PROCEED until user responds.

## Step 11: On "Continue"

Mark `[x] Code Generation` in unit progress.
Log `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]` to audit.md.
