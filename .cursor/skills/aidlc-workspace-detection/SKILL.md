---
name: aidlc-workspace-detection
description: >-
  Detect AI-DLC workspace state. Use when starting any new AI-DLC software
  development request, when the user says "start AI-DLC", "begin inception",
  or when aidlc-docs/aidlc-state.md does not exist yet. Determines if the
  project is greenfield or brownfield and whether reverse-engineering is needed.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC Workspace Detection

**Stage**: Inception — Workspace Detection (ALWAYS EXECUTE)
**Gate**: None — auto-proceeds to next stage after completion

## Step 0: Prerequisites check

Read `references/state-contract.md` and `references/audit-format.md`.

**Step 0a**: Log initial user request to `aidlc-docs/audit.md`:
```
## Workspace Detection
**Timestamp**: [ISO 8601]
**User Input**: "[Complete raw user request — never summarize]"
**AI Response**: "[Starting Workspace Detection]"
**Context**: Inception Phase — Workspace Detection — Stage Start
---
```

## Step 1: Check for existing state

Read `aidlc-docs/aidlc-state.md` if it exists.

**If exists**: Read current stage, active unit, and workstream info.
Display session-continuity resume prompt (from `.unicli-rules/common/session-continuity.md`).
Report to user: "Resuming at [current stage] — [active unit]."
Do NOT reinitialize state. Dispatch to coordinator (`aidlc-workflow`) for stage routing.

**If absent**: Proceed to Step 2 (new project setup).

## Step 2: Scan workspace (new project)

Check for existence of:
- Application code directories (`resource-inventory/`, `frontend/`, `infra/`, etc.)
- `aidlc-docs/inception/reverse-engineering/` directory and contents
- Any source code files (`.java`, `.ts`, `.py`, `.go`)

Classify:
- **Greenfield**: No existing code -> skip Reverse Engineering
- **Brownfield**: Existing code detected -> Reverse Engineering needed (unless artifacts exist)

## Step 3: Check for existing reverse-engineering artifacts

If brownfield: check `aidlc-docs/inception/reverse-engineering/` for existing artifacts.
- Artifacts present -> skip Reverse Engineering, proceed to Requirements Analysis
- Artifacts absent -> Reverse Engineering needed

## Step 4: Create initial aidlc-state.md

If state file is absent, create `aidlc-docs/aidlc-state.md` with this structure:

```markdown
# AI-DLC State Tracking

## Project Information

- **Project Name**: [detected from code or CLAUDE.md]
- **Project Type**: [Greenfield | Brownfield]
- **Start Date**: [today's date]
- **Current Stage**: Workspace Detection
- **Last Updated**: [today's date]

## AI-DLC Active Workstream

- **Branch**: [current git branch]
- **Worktree**: [current worktree path]
- **Scope**: [from user's request]
- **Jira Ticket**: TBD

## Workspace State

- **Existing Code**: [Yes | No]
- **RE Needed**: [Yes | No | Already Done]
- **Workspace Root**: [path]

## Extension Configuration

| Extension | Mode |
|-----------|------|
| ADR Governance | Disabled |
| Security Baseline | Disabled |
| Property-Based Testing | Disabled |
| TMF Compliance | Disabled |

## Inception Progress

- [ ] Workspace Detection
- [ ] Reverse Engineering
- [ ] Requirements Analysis
- [ ] User Stories
- [ ] Workflow Planning
- [ ] Application Design
- [ ] Units Generation
```

## Step 5: Mark complete and log

Update `aidlc-docs/aidlc-state.md` — mark `[x] Workspace Detection`.

Log completion to audit.md:
```
## Workspace Detection — Complete
**Timestamp**: [ISO 8601]
**User Input**: "[auto-proceed]"
**AI Response**: "Workspace Detection complete. Project type: [type]. RE needed: [yes/no]."
**Context**: Inception — Workspace Detection — DONE
---
```

## Step 6: Present completion and next stage

Report findings to user:
- Project type (greenfield/brownfield)
- Whether RE artifacts exist
- Next stage to execute

Auto-proceed (no approval needed). Instruct user to invoke `aidlc-workflow` or the specific next skill.
