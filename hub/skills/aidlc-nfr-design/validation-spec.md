# Validation Spec — aidlc-nfr-design

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists and contains an active unit entry
- [ ] Active unit `aidlc-docs/construction/{unit}/INDEX.md` exists
- [ ] NFR Requirements stage checkbox `[x]` in unit's construction progress (skip if NFR Requirements was skipped)
- [ ] `APPROVAL-STAGE: NFR_REQUIREMENTS_APPROVED [unit={unit}]` in `aidlc-docs/audit.md`
- [ ] `aidlc-docs/construction/{unit}/nfr-requirements/nfr-requirements.md` exists

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/construction/{unit}/nfr-design/nfr-design.md` | yes (if executed) | Must map each NFR requirement to a design pattern; must include: caching strategy (Redis/in-process), circuit breaker/retry patterns, observability integration (Micrometer/OpenTelemetry), security controls (JWT, RBAC, rate limiting), data partitioning/archival (TimescaleDB if time-series) |
| `aidlc-docs/audit.md` | yes (append) | Must contain start log entry and `APPROVAL-STAGE: NFR_DESIGN_APPROVED [unit={unit}]` on completion |

**Conditional artefact**:
- If vague-keyword scan finds `depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`: create `aidlc-docs/construction/{unit}/nfr-design-questions.md`. All `[Answer]:` tags must be filled and incorporated before approval gate.

**Skip artefact**: If skipped (because NFR Requirements was skipped), `aidlc-docs/audit.md` must contain skip entry and `[x] NFR Design` marked in unit's construction progress.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: NFR_REQUIREMENTS_APPROVED [unit={unit}]`
- Emit on completion: `APPROVAL-STAGE: NFR_DESIGN_APPROVED [unit={unit}]`
- Marker is appended to `aidlc-docs/audit.md`
- `[x] NFR Design` is marked in the unit's `## Construction Progress`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| NFR Requirements was skipped | Write skip entry; mark `[x] NFR Design`; return |
| `NFR_REQUIREMENTS_APPROVED [unit={unit}]` not in audit.md | Delegate to `aidlc-workflow`; return |
| `nfr-requirements.md` absent | Halt; report missing prerequisite artifact; do NOT proceed |
| Vague-keyword scan finds issues | Create questions file; wait for all answers; update artifact before gate |
| User selects "Option 1 — Request Changes" at gate | Update artifact; re-present the same gate (do NOT advance) |
