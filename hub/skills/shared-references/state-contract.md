# AI-DLC State Contract

## State SSOT: `aidlc-docs/aidlc-state.md`

The coordinator and all stage skills read/write this file for workflow state.

## Read: Coordinator reads ONLY these header sections

```
## Project Information
## AI-DLC Active Workstream
## Workspace State
## Extension Configuration
```

DO NOT read Phase 1 completion history, Branch Lineage, or per-unit build logs — these are large and rarely needed by the coordinator.

## Write: What each stage writes

| Stage | Writes |
|-------|--------|
| aidlc-workspace-detection | Creates initial stub if absent; sets `Current Stage: Workspace Detection → done` |
| All inception stages | Sets `[ ] → [x]` on their stage checkbox row |
| All construction stages | Sets `[ ] → [x]` on unit's stage checkbox row |
| Any CONDITIONAL SKIP | Writes `SKIP: <stage> — <rationale>` to audit.md |
| aidlc-build-and-test | Sets unit to complete only AFTER `GATE-QA: PASS` + `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED` |
| aidlc-requirements-analysis | Updates `## Extension Configuration` block with opt-in answers |

## Stage Checkbox Pattern

```markdown
**U24 Construction**:
- [x] Functional Design — SKIP (no new data model)
- [x] NFR Requirements
- [x] NFR Design
- [x] Infrastructure Design — SKIP (no new infra)
- [ ] Code Generation
- [ ] Build and Test
```

## Active Workstream Section

```markdown
## AI-DLC Active Workstream (U24 — Example)

- **Branch**: feature/ai-dlc-u24-example
- **Worktree**: git-worktrees/feature/ai-dlc-u24-example
- **Scope**: [brief description]
- **Jira Ticket**: NWAE-XXXX
```

## Extension Configuration Section

```markdown
## Extension Configuration

| Extension | Mode |
|-----------|------|
| ADR Governance | Enabled (Full) |
| Security Baseline | Disabled |
| Property-Based Testing | Enabled (Full) |
| TMF Compliance | Enabled (Full) |
```

`Mode` values: `Disabled` | `Enabled (Partial)` | `Enabled (Full)`

Before enforcing any extension rule: check this table. Skip disabled extensions; log the skip in audit.md.
