# Validation Spec — aidlc-nfr-requirements

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists and contains an active unit entry
- [ ] Active unit `aidlc-docs/construction/{unit}/INDEX.md` exists
- [ ] Functional Design stage status `done` or `skipped` for active unit
- [ ] `audit.md` tail contains `APPROVAL-STAGE: FUNCTIONAL_DESIGN_APPROVED [unit={unit}]` or `SKIP: Functional Design — {unit} — ...`
- [ ] Execute-IF criteria evaluated (skip if no NFR requirements and tech stack already determined)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/construction/{unit}/nfr-requirements/nfr-requirements.md` | yes (if executed) | Must cover: performance (latency/throughput targets, SLA/SLO), security (threat model, auth/authz, data classification), scalability (horizontal/vertical), tech stack selection (with rationale), observability (logging, metrics, tracing) |
| `aidlc-docs/audit.md` | yes (append) | Must contain start log entry and `APPROVAL-STAGE: NFR_REQUIREMENTS_APPROVED [unit={unit}]` on completion |

**Conditional artefact**:
- If vague-keyword scan finds `depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`: create `aidlc-docs/construction/{unit}/nfr-requirements-questions.md`. All `[Answer]:` tags must be filled and incorporated before approval gate.

**Extension dependency**: If `Security Baseline: Enabled (Full)` in state, `extensions/security/baseline/security-baseline.md` rules are applied to the security section.

**Skip artefact**: If skipped, `aidlc-docs/audit.md` must contain skip entry and `[x] NFR Requirements` marked in unit's construction progress.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: FUNCTIONAL_DESIGN_APPROVED [unit={unit}]` or `SKIP: Functional Design — {unit} — ...`
- Emit on completion: `APPROVAL-STAGE: NFR_REQUIREMENTS_APPROVED [unit={unit}]`
- Marker is appended to `aidlc-docs/audit.md`
- `[x] NFR Requirements` is marked in the unit's `## Construction Progress`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| Active unit not identified | Delegate to `aidlc-workflow`; return |
| Execute-IF not met (should skip) | Write skip entry; mark `[x] NFR Requirements`; return |
| Security Baseline extension enabled but security section incomplete | Apply security-baseline.md rules; block gate until security requirements are documented |
| Vague-keyword scan finds issues | Create questions file; wait for all answers; update artifact before gate |
| User selects "Option 1 — Request Changes" at gate | Update artifact; re-present the same gate (do NOT advance) |
