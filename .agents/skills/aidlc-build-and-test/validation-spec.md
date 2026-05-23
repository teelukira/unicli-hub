# Validation Spec — aidlc-build-and-test

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists and contains an active unit entry
- [ ] Code Generation stage checkbox `[x]` in unit's construction progress
- [ ] `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]` in `aidlc-docs/audit.md`
- [ ] `aidlc-docs/construction/{unit}/INDEX.md` exists

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/audit.md` — `GATE-QA:` entry | yes | Must be `GATE-QA: PASS`; any `GATE-QA: FAIL` blocks gate |
| `aidlc-docs/audit.md` — `GATE-TMF:` entry | conditional | Required if unit uses TMF API AND `TMF Compliance: Enabled (Full)`. Must be `GATE-TMF: PASS`, `GATE-TMF: CONDITIONAL PASS`, or `GATE-TMF: N/A`. `GATE-TMF: FAIL` blocks gate. |
| `aidlc-docs/audit.md` — `GATE-WEB:` entry | conditional | Required if unit has frontend or mixed scope. Must be `GATE-WEB: PASS`, `GATE-WEB: CONDITIONAL PASS`, or `GATE-WEB: N/A`. `GATE-WEB: FAIL` blocks gate. |
| `aidlc-docs/audit.md` — subagent invocation logs | yes | Must contain `## Subagent Invocation — qa-tester` log block with ISO 8601 timestamp, input, result, and context |
| `aidlc-docs/construction/{unit}/INDEX.md` | yes (verify) | If `ADR Governance: Enabled (Full)`: `**Relates-To-ADR**:` line must be present — BLOCKING if absent |
| `aidlc-docs/audit.md` — `APPROVAL-STAGE:` | yes | Must contain `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` after all gates pass and user approves |
| `aidlc-docs/audit.md` — `JIRA-REVIEW:` | yes | Must contain `JIRA-REVIEW: NWAE-### [unit={unit}]` (or failure log) after Jira Review transition (Step 10) |
| `aidlc-audit.md` — `MR-CREATED:` | conditional | If user approves MR creation: `MR-CREATED: !{mr-number} [{ticket-keys}]` appended to audit.md |

**PBT enforcement**: If `Property-Based Testing: Enabled (Full)`, qa-tester report must confirm jqwik PBT tests exist. Missing PBT tests are BLOCKING — add tests and re-run qa-tester before gate.

**Git discipline check** (before MR): `git log --oneline origin/main..HEAD` and `git diff --stat origin/main...HEAD` must both be non-empty. If both empty, halt MR creation and report issue.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]`
- **Sub-gate markers** (written to `aidlc-docs/audit.md` by subagent invocations, not by user approval):
  - `GATE-QA: PASS | FAIL`
  - `GATE-TMF: PASS | CONDITIONAL PASS | FAIL | N/A`
  - `GATE-WEB: PASS | CONDITIONAL PASS | FAIL | N/A`
- Emit on user approval (ONLY after all required gates pass): `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]`
- Marker is appended to `aidlc-docs/audit.md`
- `[x] Build and Test` is marked in the unit's `## Construction Progress`
- Unit status updated to complete in `aidlc-docs/aidlc-state.md`

## Subagent dispatch contract

- **BLOCKING subagents** (all must complete and PASS before user approval gate):
  - `qa-tester` — ALWAYS dispatched. `GATE-QA: PASS` required.
  - `tmf-compliance-reviewer` — if unit uses TMF API AND `TMF Compliance: Enabled (Full)`. `GATE-TMF: PASS | CONDITIONAL PASS` required.
  - `web-integration-tester` — if unit has frontend or mixed scope. `GATE-WEB: PASS | CONDITIONAL PASS` required.

- **Conditional subagents**: none beyond the above (all three are conditionally required or always required)

## Failure modes

| Condition | Action |
|---|---|
| `CODE_GENERATION_APPROVED [unit={unit}]` not in audit.md | Delegate to `aidlc-workflow`; return |
| `GATE-QA: FAIL` | Present failure details; do NOT proceed to gate; wait for user fix and qa-tester retry |
| `GATE-TMF: FAIL` | Present NC list; BLOCKING — fixes required; re-run tmf-compliance-reviewer before gate |
| `GATE-WEB: FAIL` | Present browser test details; BLOCKING — fixes required; re-run web-integration-tester before gate |
| PBT tests missing (when extension enabled) | Block gate; require jqwik PBT test additions and qa-tester re-run |
| `**Relates-To-ADR**:` missing in INDEX.md (ADR Governance enabled) | BLOCKING — add backlinks before proceeding |
| Jira Review transition fails | Log failure per `common/jira-integration.md` §4; do NOT block stage advancement |
| `git log` and `git diff` both empty before MR | Halt MR creation; report branch/push order issue; do NOT call `gitlab_create_merge_request` |
| User selects "Option 1 — Request Changes" at gate | Re-run relevant subagent(s) after fix; re-present gate only when all gates re-pass |
