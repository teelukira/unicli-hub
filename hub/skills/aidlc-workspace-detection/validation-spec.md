# Validation Spec — aidlc-workspace-detection

## Preconditions (machine-checkable)

- [ ] Workspace root is accessible (files readable)
- [ ] `aidlc-docs/` directory accessible for state file creation

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/aidlc-state.md` | yes (created if absent) | Must contain `## Project Information`, `## AI-DLC Active Workstream`, `## Workspace State`, `## Extension Configuration`, `## Inception Progress` sections |
| `aidlc-docs/audit.md` | yes (append) | Must contain a `## Workspace Detection` log entry with ISO 8601 timestamp and raw user input |

**If state file already exists** (resume path): no new artefact is created; skill dispatches back to `aidlc-workflow` for stage routing.

## Gate marker contract

- **No `APPROVAL-STAGE` marker is emitted.** This stage auto-proceeds without explicit user approval (per SKILL.md Step 6).
- On completion: marks `[x] Workspace Detection` in `aidlc-docs/aidlc-state.md` and appends a completion log entry to `aidlc-docs/audit.md`.
- Pre-marker required: none (first stage in workflow).

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none
- On resume (state.md exists): delegates to `aidlc-workflow` via Task tool to handle stage routing.

## Failure modes

| Condition | Action |
|---|---|
| `aidlc-state.md` already exists | Read state; display session-continuity resume prompt; delegate to `aidlc-workflow`; do NOT reinitialize state |
| Unable to read workspace (permissions) | Halt; report error; ask user to verify workspace path |
| Workspace is brownfield and no RE artifacts | Classify as brownfield + RE needed; record in state.md; auto-proceed |
| Workspace is brownfield with existing RE artifacts | Classify as brownfield + RE already done; record in state.md; auto-proceed |
