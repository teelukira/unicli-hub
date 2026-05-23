# hub/ — AI-DLC + unicli-hub SSOT

This directory is the Single Source of Truth for the ORION AI-DLC workflow framework.
`./sync.sh --fix` regenerates all derived files from here.

See also: `hub/project-context.md` (project stack/context), `hub/core-workflow.md` (full workflow rules).

---

## Architecture Overview

```
CLAUDE.md (always-loaded, < 8 KB)
  └─ "For any software dev request → invoke aidlc-workflow skill"

aidlc-workflow skill (coordinator, phase: coordinator)
  ├─ reads aidlc-docs/aidlc-state.md (state SSOT)
  └─ dispatches → aidlc-<stage> skill via Task tool

aidlc-<stage> skills (atomic, on-demand)
  ├─ SKILL.md — frontmatter (phase/stage/per-unit/…) + step-by-step instructions
  ├─ validation-spec.md — machine-checkable preconditions, artefact contracts, gate markers
  ├─ reads hub/<phase>/<stage>.md (full rules)
  └─ dispatches → domain subagents (codegen-*, qa-tester, etc.) via Task tool
```

**Progressive disclosure levels:**
- L1: skill `description` in YAML frontmatter — always in context (~2 lines)
- L2: `SKILL.md` body — loaded when Claude decides skill is relevant
- L3: `references/*.md` + `hub/<stage>.md` — loaded on-demand within the skill

---

## Skill Catalog

### Coordinator

| Skill | phase | Trigger description | Gate |
|-------|-------|---------------------|------|
| `aidlc-workflow` | coordinator | AI-DLC workflow coordinator. Use FIRST whenever the user requests software development, says "start AI-DLC", "continue AI-DLC", "resume my project", "what's next in AI-DLC". | passthrough |

### Inception Stage Skills

| # | Skill | phase | per-unit | Stage file | BLOCKING subagents | Gate |
|---|-------|-------|----------|------------|---------------------|------|
| 1 | `aidlc-workspace-detection` | inception | false | `inception/workspace-detection.md` | — | auto |
| 2 | `aidlc-reverse-engineering` | inception | false | `inception/reverse-engineering.md` | `aidlc-researcher` (advisory) | explicit |
| 3 | `aidlc-requirements-analysis` | inception | false | `inception/requirements-analysis.md` | `tmf-knowledge-ingest` (cond.) | explicit |
| 4 | `aidlc-user-stories` | inception | false | `inception/user-stories.md` | — | explicit ×2 |
| 5 | `aidlc-workflow-planning` | inception | false | `inception/workflow-planning.md` | — | explicit |
| 6 | `aidlc-application-design` | inception | false | `inception/application-design.md` | `aidlc-researcher` (advisory), `adr-curator` (cond.) | explicit |
| 7 | `aidlc-units-generation` | inception | false | `inception/units-generation.md` | — | explicit ×2 |

### Construction Stage Skills (per-unit loop)

| # | Skill | phase | per-unit | Stage file | BLOCKING subagents | Gate |
|---|-------|-------|----------|------------|---------------------|------|
| 8 | `aidlc-functional-design` | construction | true | `construction/functional-design.md` | `adr-curator` (cond.) | 2-option |
| 9 | `aidlc-nfr-requirements` | construction | true | `construction/nfr-requirements.md` | — | 2-option |
| 10 | `aidlc-nfr-design` | construction | true | `construction/nfr-design.md` | — | 2-option |
| 11 | `aidlc-infrastructure-design` | construction | true | `construction/infrastructure-design.md` | `codegen-iac` (cond.) | 2-option |
| 12 | `aidlc-code-generation` | construction | true | `construction/code-generation.md` | `codegen-backend/frontend/db/iac` (BLOCKING by scope) | 2-option ×2 |
| 13 | `aidlc-build-and-test` | construction | true | `construction/build-and-test.md` | `qa-tester` (ALWAYS), `tmf-compliance-reviewer` (cond.), `web-integration-tester` (cond.) | 2-option after all gates PASS |
| 14 | `aidlc-operations` | operations | false | `operations/operations.md` | — | placeholder |

### Cross-Cutting Skills

| Skill | phase | Trigger description |
|-------|-------|---------------------|
| `aidlc-adr-memory-sync` | cross-cutting | Sync ADR index to Serena memory. Auto-triggered after any ADR change. |
| `hub-upstream-sync` | cross-cutting | Pull methodology rule updates from awslabs/aidlc-workflows with per-file diff review. Trigger: "upstream sync", "check for aidlc updates", "update from aws aidlc". |

---

## hub/common/ Category Reference

| File | Category |
|------|----------|
| `gate-protocol.md`, `approval-gates.md` | protocols |
| `adr-conventions.md`, `terminology.md`, `depth-levels.md`, `codegen-principles.md`, `process-overview.md`, `aidlc-docs-unit-conventions.md`, `git-worktree-conventions.md`, `ascii-diagram-standards.md` | conventions |
| `error-handling.md`, `overconfidence-prevention.md`, `question-format-guide.md`, `content-validation.md`, `workflow-changes.md`, `session-continuity.md`, `welcome-message.md` | protocols/conventions hybrid |
| `jira-integration.md`, `tool-matrix.md` | integrations |

---

## State Machine (coordinator logic)

```
read aidlc-docs/aidlc-state.md (header only)
↓
state file absent? YES → welcome → dispatch aidlc-workspace-detection → return
↓
session start? → display "Welcome back" + resume summary
↓
pending approval in audit.md? YES → re-display 2-option message → wait → return
↓
Inception complete? NO → iterate: ws-detect → re → req → stories → plan → app-design → units
↓
Construction active? YES → per-unit loop: fd → nfrR → nfrD → infD → cg → bt
  Unit complete? → advance to next unit
↓
All units complete? → dispatch aidlc-operations
```

---

## v2 Frontmatter Schema (all aidlc-* skills)

| Field | Values | Purpose |
|-------|--------|---------|
| `phase` | `inception` / `construction` / `operations` / `coordinator` / `cross-cutting` | AI-DLC lifecycle phase |
| `stage` | skill name without `aidlc-` prefix | Stage identifier |
| `per-unit` | `true` / `false` | Runs once per Construction unit |
| `human-clarification` | `required` / `optional` / `none` | Gate interaction level |
| `plan-creation` | `true` / `false` | Skill has a planning sub-step |
| `plan-verification` | `true` / `false` | Skill verifies a generated plan |
| `artefact-verification` | `true` / `false` | Skill runs external verification gates |
| `depth` | `adaptive` | Follows `hub/common/depth-levels.md` |

Each skill also ships a `validation-spec.md` sibling with machine-checkable preconditions, artefact contracts, gate marker contracts, subagent dispatch contracts, and failure modes.

---

## Adding a New `aidlc-*` Skill

1. **Create folder**: `hub/skills/aidlc-<name>/`

2. **Write `SKILL.md`** with required frontmatter:
   ```yaml
   ---
   name: aidlc-<name>
   description: >-
     [What the skill does] + [When to use it with trigger phrases].
   allowed-tools: [Read, Edit, Write]
   phase: <inception|construction|operations|cross-cutting>
   stage: <name>
   per-unit: <true|false>
   human-clarification: <required|optional|none>
   plan-creation: false
   plan-verification: false
   artefact-verification: false
   depth: adaptive
   ---
   ```

3. **Write `validation-spec.md`** — see `aidlc-code-generation/validation-spec.md` as reference. Include:
   - Preconditions (machine-checkable)
   - Artefact contract table
   - Gate marker contract (pre-marker required + emit on completion)
   - Subagent dispatch contract
   - Failure modes table

4. **Body checklist** (SKILL.md must contain):
   - [ ] Step 0: read state-contract.md, verify prereqs, add depth-levels.md cross-reference
   - [ ] Step 1: audit log entry (ISO-8601 + raw input) + load `hub/<phase>/<stage>.md`
   - [ ] Execute logic
   - [ ] Approval gate (standardized 2-option for Construction; explicit for Inception)
   - [ ] On approval: update state.md checkbox + write `APPROVAL-STAGE: <NAME>_APPROVED` to audit.md

5. **Regenerate**: `./sync.sh --fix`

6. **Update coordinator** (`hub/skills/aidlc-workflow/SKILL.md`) if this is a new workflow stage.

7. **Update `hub/README.md`** — add row to catalog table.

---

## Verification Checklist

| Test | What to verify | Pass condition |
|------|---------------|----------------|
| F.1 Trigger matrix | Each aidlc-* skill fires on intended prompts | 100% hit, 0 false positives |
| F.2 State-machine | Seed state.md at each stage; "what's next?" → correct skill | Correct dispatch for all 14 states |
| F.3 Subagent dispatch | Run aidlc-build-and-test on known-clean unit | qa-tester + gate markers in audit.md |
| F.4 sync.sh idempotence | `--fix` then `--check` | `--check` exits 0 |
| F.5 Size budget | CLAUDE.md and each SKILL.md | CLAUDE.md < 8 KB; SKILL.md < 12 KB |
| F.6 One-unit regression | Full Inception+Construction round-trip | All gates pass, audit markers correct |
| F.7 Hook continuity | adr_backlink_check, state_audit, plan_checkbox_tracker | Hooks fire; violations blocked |
