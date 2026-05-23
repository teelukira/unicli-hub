---
name: aidlc-build-and-test
description: >-
  Run per-unit AI-DLC Build and Test with BLOCKING subagent gates. Use
  immediately after Code Generation completes for the active unit. Invokes
  qa-tester (always BLOCKING), tmf-compliance-reviewer (BLOCKING if TMF unit
  and TMF Compliance extension enabled), and web-integration-tester (BLOCKING
  if frontend or mixed unit).
allowed-tools: [Read, Edit, Write, Bash, Task]
phase: construction
stage: build-and-test
per-unit: true
human-clarification: required
plan-creation: false
plan-verification: true
artefact-verification: true
depth: adaptive
---

# AI-DLC Build and Test

**Stage**: Construction — Build and Test (ALWAYS EXECUTE per unit)
**Gate**: Standardized 2-option approval ONLY AFTER all subagent gates PASS
**HITL Gate Reference**: `hub/common/gate-protocol.md`

## Prerequisite check (Step 0)

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

Read `references/state-contract.md`. Identify active unit.
Verify: Code Generation `[x]` AND `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]` in audit.md.
If not → delegate to `aidlc-workflow` and return.

## Step 1: Log start and load rules

Append to audit.md. Read `hub/construction/build-and-test.md`.

## Step 2: Determine verification gate checklist

Read `aidlc-docs/aidlc-state.md` Extension Configuration and unit type:

```
Checklist:
[x] qa-tester — ALWAYS REQUIRED
[ ] tmf-compliance-reviewer — REQUIRED if (unit uses TMF API AND TMF Compliance: Enabled (Full))
[ ] web-integration-tester — REQUIRED if (unit has frontend/mixed scope)
```

ADR Integrity Gate (if ADR Governance: Enabled (Full)):
- Verify `**Relates-To-ADR**:` present in `aidlc-docs/construction/{unit}/INDEX.md`
- If missing: BLOCKING — add backlinks before proceeding

## Step 3: Invoke qa-tester (ALWAYS BLOCKING)

```
Task({
  description: "QA verification for {unit}",
  prompt: "You are the qa-tester agent. Independently verify build and tests for unit {unit-name}. Run: ./gradlew build (or npm run build for frontend). Run all tests. Report: PASS (all tests green, build clean) or FAIL (with error details). Do NOT skip tests. Output a structured report.",
  subagent_type: "qa-tester"
})
```

Log to audit.md:
```
## Subagent Invocation — qa-tester
**Timestamp**: [ISO 8601]
**Input**: "QA verification for {unit}"
**Result**: PASS | FAIL
**Context**: Build and Test — {unit} — GATE-QA
---
```

Write `GATE-QA: PASS` or `GATE-QA: FAIL` to audit.md.

**If FAIL**: Present failure details. DO NOT proceed. Wait for user to fix and retry.

## Step 4: Invoke tmf-compliance-reviewer (CONDITIONAL BLOCKING)

If TMF unit AND TMF Compliance extension Enabled:

First read `references/tmf-compliance.md` for applicable rules.

```
Task({
  description: "TMF compliance review for {unit}",
  prompt: "You are the tmf-compliance-reviewer agent. Perform full TMF-A through TMF-N (14 rules) verification for unit {unit-name}. Scope: [TMF639/634/641/702 as applicable]. You MUST adhere to the 3-Pillar Verification Architecture (Pillar 1: API Spec, Pillar 2: SID Schema, Pillar 3: CTK Conformance) by running or parsing the respective reports, and prioritize atom-tmf-kb-mcp tools. Undergo strict evaluation: ONLY PASS or FAIL is allowed (no CONDITIONAL PASS). Output review-report.md, compliance-evidence.md, and component-mapping.md under specs/tmf/{unit}/.",
  subagent_type: "tmf-compliance-reviewer"
})
```

Log invocation to audit.md. Write `GATE-TMF: PASS | FAIL` to audit.md.

**If FAIL**: Present NC list. BLOCKING — fixes required before proceeding.
**If N/A**: Write `GATE-TMF: N/A` and document why.

## Step 5: Invoke web-integration-tester (CONDITIONAL BLOCKING)

If unit has frontend or mixed scope:

```
Task({
  description: "Web integration test for {unit}",
  prompt: "You are the web-integration-tester agent. Run Playwright E2E tests for unit {unit-name}. Start local dev server per CLAUDE.md instructions. Test the golden path and key edge cases. Report: PASS, CONDITIONAL PASS, or FAIL with browser test details.",
  subagent_type: "web-integration-tester"
})
```

Log invocation. Write `GATE-WEB: PASS | CONDITIONAL PASS | FAIL | N/A` to audit.md.

## Step 6: Property-Based Testing enforcement

If `Property-Based Testing: Enabled (Full)`:
Verify jqwik PBT tests exist in qa-tester's report. If missing: BLOCKING — add PBT tests and re-run qa-tester.

## Step 7: All-gate check

**DO NOT present completion message until ALL required gates are PASS (or N/A):**
- `GATE-QA: PASS` required
- `GATE-TMF: PASS | N/A` required
- `GATE-WEB: PASS | CONDITIONAL PASS | N/A` required

If any gate is FAIL: present failure. Wait for fix. Retry that gate.

## Step 8: Standardized 2-option approval gate

ONLY when all gates pass:

```
## Build and Test Complete — {Unit Name}

**Gate Results**:
- GATE-QA: {result}
- GATE-TMF: {result}
- GATE-WEB: {result}

{Extension compliance summary}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change.
**Option 2 — Continue (Unit Complete)**: Mark unit complete and advance.
```

Log raw input. DO NOT PROCEED until user responds.

## Step 9: On "Continue"

Mark `[x] Build and Test` in unit progress.
Log `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` to audit.md.
Update unit status to complete in `aidlc-docs/aidlc-state.md`.

## Step 10: Jira Review transition (MANDATORY)

Build and Test 완료 = 코드 완성 + QA 통과 → 티켓을 검토(Review) 상태로 전이.
Human reviewer(개발자)가 MR을 merge하면 Done/Closed로 최종 처리한다.

1. Read `common/jira-integration.md` §3a. Read unit's `**Jira Ticket**` entries from `aidlc-docs/aidlc-state.md`.
2. Transition each ticket to Review using `transition_id_review` (config: `"111"` — "Resolve" → 검토).
3. Log `JIRA-REVIEW: NWAE-### [unit={unit}]` to audit.md for each ticket.

On failure: log per §4 — do NOT block advancement.

## Step 11: MR creation prompt

**Git discipline (MANDATORY)** — see `common/git-worktree-conventions.md`, `docs/conventions/gitlab-mr-workflow.md`:

- Commits must be on the feature/fix branch, **not** on `main`.
- **Do not** `git merge` the branch into local `main` before opening the MR.
- Before creating the MR, from the branch worktree:
  ```bash
  git fetch origin
  git log --oneline origin/main..HEAD
  git diff --stat origin/main...HEAD
  ```
  If both are empty, **stop** — fix branch/push order before MR (otherwise GitLab shows no changes).

Present MR summary to user:

```
## MR 준비 완료 — {Unit Name}

**Jira Tickets**: {space-separated ticket keys, e.g. NWAE-595 NWAE-596}
**Branch**: feature/{branch-name}
**Suggested MR title**: feat({unit-id}): {간결한 기능 제목}

MR을 생성할까요? (Y/N)
```

On yes:
1. Render MR body (`common/jira-integration.md` §6 Render Contract 참조):
   ```bash
   python3 scripts/render-ai-dlc-remote-templates.py --target gitlab-body --values-file /tmp/vars.json
   ```
2. Call `gitlab_create_merge_request` with a concise feature-focused title (no Jira keys — keys live in the rendered body via `{jira_keys}`). Set `description` to the rendered body stdout. The fill-in sections (변경 요약, 관련 ADR, 영향 범위, 검증, 리뷰어 참고 사항) in `.gitlab/merge_request_templates/default.md` are completed by the developer after MR creation.
3. Log `MR-CREATED: !{mr-number} [{ticket-keys}]` to audit.md.
4. After the user merges on GitLab (or approves `glab mr merge`), sync local main with **`git checkout main && git pull origin main` only** — not `git merge` on main.
