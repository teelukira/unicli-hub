# Validation Spec — aidlc-workflow-planning

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `[x] Requirements Analysis`
- [ ] `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED` in `aidlc-docs/audit.md`
- [ ] `aidlc-docs/inception/requirements/requirements.md` exists

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/inception/plans/workflow-plan.md` | yes | Must contain: stage execution decision table (Execute/Skip per stage), depth assignments (Minimal/Standard/Comprehensive), Mermaid workflow diagram (syntax validated per content-validation.md), multi-package change sequence (brownfield only) |
| `aidlc-docs/audit.md` | yes (append) | Must contain start log entry and `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED` on completion |

**Content validation requirement**: Mermaid diagram syntax MUST be validated before writing the file (per `references/content-validation.md`). If syntax invalid, halt and fix before presenting to user.

## Gate marker contract

- Expected pre-marker: `APPROVAL-STAGE: REQUIREMENTS_ANALYSIS_APPROVED` (or `APPROVAL-STAGE: USER_STORIES_APPROVED` if user stories were executed)
- Emit on completion: `APPROVAL-STAGE: WORKFLOW_PLANNING_APPROVED`
- Marker is appended to `aidlc-docs/audit.md` (no `[unit=...]` suffix)
- `[x] Workflow Planning` is marked in `aidlc-docs/aidlc-state.md`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

## Failure modes

| Condition | Action |
|---|---|
| `[x] Requirements Analysis` not present | Delegate to `aidlc-workflow`; return |
| Mermaid diagram syntax invalid | Fix syntax before writing file; do NOT write invalid content |
| User overrides a stage inclusion/exclusion decision | Update decision table and diagram per user's override; re-present gate |
| User selects "Request Changes" at gate | Revise workflow plan and re-present gate (do NOT advance) |
