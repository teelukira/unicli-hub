# Validation Spec — aidlc-reverse-engineering

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists with `Workspace State.Existing Code = Yes`
- [ ] `aidlc-docs/inception/reverse-engineering/` is absent or empty
- [ ] Workspace Detection stage checkbox `[x]` in `aidlc-docs/aidlc-state.md`

## Artefact contract

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/inception/reverse-engineering/business-overview.md` | yes | Must cover business transactions of the system |
| `aidlc-docs/inception/reverse-engineering/architecture.md` | yes | Must include C4 context and container diagrams |
| `aidlc-docs/inception/reverse-engineering/code-structure.md` | yes | Must document package/module structure |
| `aidlc-docs/inception/reverse-engineering/api-docs.md` | yes | Must list endpoints and contracts |
| `aidlc-docs/inception/reverse-engineering/component-inventory.md` | yes | Must enumerate all components |
| `aidlc-docs/inception/reverse-engineering/interaction-diagrams.md` | yes | Must depict business transactions across components |
| `aidlc-docs/inception/reverse-engineering/tech-stack.md` | yes | Must list all major technologies |
| `aidlc-docs/inception/reverse-engineering/dependencies.md` | yes | Must document external and internal dependencies |
| `aidlc-docs/audit.md` | yes (append) | Must contain `## Reverse Engineering` start log entry and `APPROVAL-STAGE: REVERSE_ENGINEERING_APPROVED` on completion |

## Gate marker contract

- Expected pre-marker: none required (first conditional Inception stage after Workspace Detection)
- Emit on completion (after user approval): `APPROVAL-STAGE: REVERSE_ENGINEERING_APPROVED`
- Marker is appended to `aidlc-docs/audit.md` (no `[unit=...]` suffix — this is not a per-unit stage)
- `[x] Reverse Engineering` is marked in `aidlc-docs/aidlc-state.md`

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: `aidlc-researcher` — if unfamiliar tech stack encountered (Step 4). Advisory only, not blocking the approval gate.

## Failure modes

| Condition | Action |
|---|---|
| Prerequisites not met (not brownfield, or RE artifacts already exist) | Delegate back to `aidlc-workflow` via Task tool; return |
| User selects "Request Changes" at gate | Revise artifacts and re-present approval gate (do NOT advance) |
| Unfamiliar tech stack detected | Invoke `aidlc-researcher` subagent; wait for completion summary; incorporate into artifacts |
