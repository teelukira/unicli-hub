# Validation Spec — aidlc-requirements-analysis

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `[x] Workspace Detection`
- [ ] Prior stage approval in `aidlc-docs/audit.md`: `APPROVAL-STAGE: REVERSE_ENGINEERING_APPROVED` (brownfield) or Workspace Detection completion log (greenfield)

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/inception/requirements/requirements.md` | yes | Must contain functional requirements, non-functional requirements (if standard/comprehensive depth), risks, and constraints |
| `aidlc-docs/aidlc-state.md` (Extension Configuration) | yes (update) | `## Extension Configuration` table updated with user opt-in answers for all 4 extensions |
| `aidlc-docs/audit.md` | yes (append) | Must contain `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED` and `JIRA-CREATED: NWAE-### [unit=...]` (or failure log per §4) on completion |
| `aidlc-docs/aidlc-state.md` (Jira Ticket) | yes (update) | `**Jira Ticket**: NWAE-###` line added to active unit section (or placeholder on Jira failure) |

**Conditional artefact**:
- If clarifying questions asked: `aidlc-docs/audit.md` must contain the user's raw answers before requirements document is finalized.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: REVERSE_ENGINEERING_APPROVED` (brownfield) or Workspace Detection complete entry (greenfield)
- Emit on completion: `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED`
- Marker is appended to `aidlc-docs/audit.md` (no `[unit=...]` suffix)
- `[x] Requirements Analysis` is marked in `aidlc-docs/aidlc-state.md`
- **MANDATORY**: Jira ticket creation (Step 10) must complete (or log failure) before stage is considered done. `APPROVAL-JIRA-CREATE: granted [unit=...]` must appear in audit.md prior to calling `jira_create_issue`.

## Subagent dispatch contract

- **BLOCKING subagents**: `tmf-knowledge-ingest` — if TMF-standard unit and `docs/tmf-oracle/` chunks are stale or missing (Step 6). Must complete before extension opt-in step.
- **Conditional subagents**: none beyond the above

## Failure modes

| Condition | Action |
|---|---|
| `[x] Workspace Detection` not present in state | Delegate to `aidlc-workflow`; return |
| TMF oracle chunks stale/missing | Invoke `tmf-knowledge-ingest` (BLOCKING); wait for completion before continuing |
| Jira ticket creation fails | Log placeholder per `common/jira-integration.md` §4; do NOT block stage advancement |
| User selects "Request Changes" at gate | Revise requirements and re-present gate (do NOT advance) |
| `APPROVAL-JIRA-CREATE` not obtained | Block Jira ticket creation; wait for user to confirm preview before calling API |
