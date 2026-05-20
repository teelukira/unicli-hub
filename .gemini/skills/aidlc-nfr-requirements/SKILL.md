---
name: aidlc-nfr-requirements
description: >-
  Run per-unit AI-DLC NFR Requirements assessment. Use when the active
  construction unit has performance, security, scalability, or tech-stack
  selection requirements.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC NFR Requirements

**Stage**: Construction — NFR Requirements (CONDITIONAL, per-unit)
**Gate**: Standardized 2-option approval
**HITL Gate Reference**: `.unicli-rules/common/gate-protocol.md`

## Prerequisite check (Step 0)

Read `references/state-contract.md`. Identify active unit.

Evaluate Execute-IF / Skip-IF:
- **Execute IF**: Performance requirements; security considerations; scalability concerns; tech-stack selection required
- **Skip IF**: No NFR requirements; tech stack already fully determined

If skip: write skip to audit.md. Mark `[x] NFR Requirements`. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `.unicli-rules/construction/nfr-requirements.md`.

## Step 2: Check security extension

Read `aidlc-docs/aidlc-state.md` Extension Configuration.
If `Security Baseline: Enabled (Full)` → read `extensions/security/baseline/security-baseline.md` for applicable rules.

## Step 3: Execute NFR assessment

Per loaded `nfr-requirements.md`:
- Performance: latency/throughput targets, SLA/SLO
- Security: threat model, auth/authz requirements, data classification
- Scalability: horizontal/vertical scaling needs, stateless/stateful
- Tech stack selection: confirm or propose stack choices with rationale
- Observability: logging, metrics, tracing requirements

Output: `aidlc-docs/construction/{unit}/nfr-requirements/nfr-requirements.md`

## Step 3b: Vague-Keyword Scan (per gate-protocol.md)

Scan the draft artifact for vague keywords (`depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`).

- **If found**: Create `aidlc-docs/construction/{unit}/nfr-requirements-questions.md` per `common/question-format-guide.md`. Notify user; wait for all `[Answer]:` tags filled. Update artifact. Then proceed to Step 4.
- **If not found**: Proceed directly to Step 4.

## Step 4: Standardized 2-option gate

```
## NFR Requirements Complete — {Unit Name}

**Artifact(s)**:
- `aidlc-docs/construction/{unit}/nfr-requirements/nfr-requirements.md`

{NFR summary table}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change. I will update the artifact and re-present this gate.
**Option 2 — Continue**: Proceed to NFR Design.
```

Log raw user input to audit.md. DO NOT PROCEED until user responds.

Mark `[x] NFR Requirements` and log `APPROVAL-STAGE: NFR_REQUIREMENTS_APPROVED [unit={unit}]` on "Continue".

