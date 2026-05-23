---
name: aidlc-nfr-design
description: >-
  Run per-unit AI-DLC NFR Design. Use when NFR Requirements was executed for
  the active construction unit and NFR patterns need to be incorporated into
  the design.
allowed-tools: [Read, Edit, Write]
phase: construction
stage: nfr-design
per-unit: true
human-clarification: required
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# AI-DLC NFR Design

**Stage**: Construction — NFR Design (CONDITIONAL, per-unit)
**Gate**: Standardized 2-option approval
**HITL Gate Reference**: `hub/common/gate-protocol.md`

## Prerequisite check (Step 0)

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

Read `references/state-contract.md`. Identify active unit.
Check `[x] NFR Requirements` in unit's construction progress.

- **Execute IF**: NFR Requirements was executed (checkbox `[x]`)
- **Skip IF**: NFR Requirements was skipped

If skip: write skip to audit.md. Mark `[x] NFR Design`. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `hub/construction/nfr-design.md`.

## Step 2: Execute NFR design

Read `aidlc-docs/construction/{unit}/nfr-requirements/nfr-requirements.md`.

Per loaded `nfr-design.md`:
- Map NFR requirements to specific design patterns
- Define caching strategy (Redis, in-process)
- Define circuit breaker / retry patterns
- Define observability integration (Micrometer, OpenTelemetry)
- Define security controls (JWT validation, RBAC, rate limiting)
- Define data partitioning and archival strategies (TimescaleDB if time-series)

Output: `aidlc-docs/construction/{unit}/nfr-design/nfr-design.md`

## Step 2b: Vague-Keyword Scan (per gate-protocol.md)

Scan the draft artifact for vague keywords (`depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`).

- **If found**: Create `aidlc-docs/construction/{unit}/nfr-design-questions.md` per `common/question-format-guide.md`. Notify user; wait for all `[Answer]:` tags filled. Update artifact. Then proceed to Step 3.
- **If not found**: Proceed directly to Step 3.

## Step 3: Standardized 2-option gate

```
## NFR Design Complete — {Unit Name}

**Artifact(s)**:
- `aidlc-docs/construction/{unit}/nfr-design/nfr-design.md`

{NFR design patterns summary}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change. I will update the artifact and re-present this gate.
**Option 2 — Continue**: Proceed to Infrastructure Design.
```

Log raw user input to audit.md. DO NOT PROCEED until user responds.

Mark `[x] NFR Design` and log `APPROVAL-STAGE: NFR_DESIGN_APPROVED [unit={unit}]` on "Continue".

