---
name: aidlc-requirements-analysis
description: >-
  Run AI-DLC Requirements Analysis with adaptive depth (minimal/standard/
  comprehensive). Use after workspace detection and optional reverse-engineering
  when requirements have not yet been captured for the current workstream. Also
  drives extension opt-in for ADR Governance, Security Baseline, Property-Based
  Testing, and TMF Compliance.
allowed-tools: [Read, Edit, Write, Task]
---

# AI-DLC Requirements Analysis

**Stage**: Inception — Requirements Analysis (ALWAYS EXECUTE — adaptive depth)
**Gate**: Explicit user approval before proceeding

## Prerequisite check (Step 0)

Read `references/state-contract.md`. Verify:
- `aidlc-docs/aidlc-state.md` exists with Workspace Detection `[x]`

If prerequisites not met -> delegate to `aidlc-workflow` and return.

## Step 1: Log start and load rules

Append start entry to `aidlc-docs/audit.md`.
Read `.unicli-rules/inception/requirements-analysis.md` for full execution steps.

## Step 2: Load extensions opt-in prompts

Read ONLY the `*.opt-in.md` files (NOT the full rule files):
- `extensions/adr/governance/adr-governance.opt-in.md`
- `extensions/security/baseline/security-baseline.opt-in.md`
- `extensions/testing/property-based/property-based-testing.opt-in.md`
- `extensions/tmf/compliance/tmf-compliance.opt-in.md`

Store them for Step 7 (extension opt-in).

## Step 3: Load context

If brownfield: load reverse-engineering artifacts from `aidlc-docs/inception/reverse-engineering/`.
Read user's request from audit.md (first entry).

## Step 4: Determine depth

Assess request complexity:
- **Minimal**: Simple, clear request with obvious scope
- **Standard**: Normal feature/unit with functional + NFR requirements
- **Comprehensive**: Complex, multi-component, high-risk change

## Step 5: Execute requirements analysis

Follow `requirements-analysis.md` steps at determined depth:
- Analyze user intent
- Capture functional requirements
- Capture non-functional requirements (if standard/comprehensive)
- Identify risks and constraints
- Ask clarifying questions using `references/question-format.md` format

Output: `aidlc-docs/inception/requirements/requirements.md`

## Step 6: TMF knowledge check

If this is a TMF-standard unit (TMF639/634/641/702):
- Check if `docs/tmf-oracle/` has relevant chunks
- If stale or missing: invoke `tmf-knowledge-ingest` subagent (BLOCKING) via Task tool
- Wait for completion before continuing

## Step 7: Extension opt-in

Present extension opt-in choices to user based on loaded opt-in prompts:

```
## Extension Configuration

Please select which extensions to enable for this workstream:

**A. ADR Governance** — [summary from adr-governance.opt-in.md]
   Enable? Y/N

**B. Security Baseline** — [summary from security-baseline.opt-in.md]
   Enable? Y/N

**C. Property-Based Testing** — [summary from property-based-testing.opt-in.md]
   Enable? Y/N

**D. TMF Compliance** — [summary from tmf-compliance.opt-in.md]
   Enable? Y/N
```

Update `aidlc-docs/aidlc-state.md` `## Extension Configuration` table with user answers.

## Step 8: Approval gate

Present completion message with standardized 2-option format:

```
## Requirements Analysis Complete

[Summary of captured requirements]

**Options**:
A. Continue to User Stories / Workflow Planning
B. Request Changes to Requirements

[Answer]: _
```

Log raw user input to audit.md. DO NOT PROCEED until approved.

## Step 9: On approval

Mark `[x] Requirements Analysis` in state.md.
Log `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED` to audit.md.

## Step 10: Jira ticket creation (MANDATORY after approval — SSOT)

Read `common/jira-integration.md` §2 and §6. Create one ticket per work item (or one per unit if work items are not explicitly separated).

**Description 렌더**:
```bash
python3 scripts/render-ai-dlc-remote-templates.py --target jira --values-file /tmp/vars.json
```
`/tmp/vars.json`에 9개 변수 작성 (`common/jira-integration.md` §6 Render Contract 참조). stdout이 `jira_create_issue`의 `description` 파라미터.

1. Preview ticket(s) to user → wait for `APPROVAL-JIRA-CREATE: granted [unit=...]`
2. Call `jira_create_issue` per config (`issue_type: 작업(Task)`), `description` = render stdout
3. Log `JIRA-CREATED: NWAE-### [unit=Uxx]` to audit.md for each ticket
4. Add `**Jira Ticket**: NWAE-###` to the unit section in `aidlc-docs/aidlc-state.md`

On failure: log placeholder per §4 of jira-integration.md — do NOT block stage advancement.
