---
name: aidlc-functional-design
description: >-
  Run per-unit AI-DLC Functional Design. Use when the active construction unit
  introduces new data models, database schemas, or complex business logic that
  needs detailed design before code generation.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC Functional Design

**Stage**: Construction — Functional Design (CONDITIONAL, per-unit)
**Gate**: Standardized 2-option approval (Request Changes / Continue)
**HITL Gate Reference**: `.unicli-rules/common/gate-protocol.md`

## Prerequisite check (Step 0)

Read `references/state-contract.md`.
Identify active unit from `aidlc-docs/aidlc-state.md` (`## AI-DLC Active Workstream`).

Evaluate Execute-IF / Skip-IF:
- **Execute IF**: New data models or schemas; complex business logic; business rules need detailed design
- **Skip IF**: Simple logic changes; no new business logic; implementation within existing schemas

If skip: write `SKIP: Functional Design — [unit] — [rationale]` to audit.md.
Mark `[x] Functional Design` in unit's construction progress. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/construction/functional-design.md`.

## Step 2: ADR consultation (MANDATORY)

Read `aidlc-docs/index/adr-index.md`. Identify any ADRs that govern the design decisions in this unit.
- ADR `Accepted` or `Accepted (Retroactive)` → follow it; cite in output
- ADR `Proposed` → flag as dependency; defer or complete it
- No ADR + architecturally significant decision → invoke `adr-curator` to draft one

## Step 3: Load context

Read unit's `aidlc-docs/construction/{unit}/INDEX.md`.
Read `aidlc-docs/inception/requirements/requirements.md`.
Read application design artifacts (if exist).

## Step 4: Execute functional design

Per loaded `functional-design.md`:
- Design data models and schemas (with SID GB922 alignment if applicable)
- Define business rules and validation logic
- Define domain events and commands
- Define error scenarios and edge cases
- Map to hexagonal architecture layers (domain, api, infrastructure)

Output: `aidlc-docs/construction/{unit}/functional-design/`

## Step 5: Update INDEX backlink (MANDATORY)

Update `aidlc-docs/construction/{unit}/INDEX.md` — ensure `**Relates-To-ADR**:` line is present:
```
**Relates-To-ADR**: [comma-separated ADR numbers, or "N/A"]
```

## Step 5b: Vague-Keyword Scan (per gate-protocol.md)

Scan the draft artifact for vague keywords (`depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`).

- **If found**: Create `aidlc-docs/construction/{unit}/functional-design-questions.md` per `common/question-format-guide.md`. Notify user of the file; wait for all `[Answer]:` tags to be filled. Read responses, update the artifact. Then proceed to Step 6.
- **If not found**: Proceed directly to Step 6.

## Step 6: Standardized 2-option approval gate

**CRITICAL**: Use EXACTLY this format. DO NOT add a third option.

```
## Functional Design Complete — {Unit Name}

**Artifact(s)**:
- `aidlc-docs/construction/{unit}/functional-design/`

{1-3 line summary}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change. I will update the artifact and re-present this gate.
**Option 2 — Continue**: Proceed to NFR Requirements (or next applicable stage).
```

Log raw user input to audit.md. DO NOT PROCEED until user responds.

## Step 7: On "Continue"

Mark `[x] Functional Design` in unit construction progress.
Log `APPROVAL-STAGE: FUNCTIONAL_DESIGN_APPROVED [unit={unit}]` to audit.md.

