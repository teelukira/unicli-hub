# PRIORITY: AI-DLC workflow (Cursor)

This file is the **slim always-on** Cursor rule. Full prose for every stage lives under `.unicli-rules/` and is loaded **on demand** inside skills — do not duplicate that material here.

## Adaptive principle

The workflow adapts to the work: only run stages that add value. Heavy checklists and stage text are **not** inlined in this rule.

## Mandatory entry (software development)

For **any** software development request (new feature, bugfix, continue AI-DLC, build/test, stage work):

1. **First**: Read `.cursor/skills/aidlc-workflow/SKILL.md` and follow it.
2. **State SSOT**: `aidlc-docs/aidlc-state.md`
3. **Skill index & architecture**: `aidlc-docs/SKILLS.md`
4. **Full cross-CLI workflow reference** (read when you need the complete stage list or governance text): `.unicli-rules/core-workflow.md`

## Rule details directory

All stage-specific instructions live under `.unicli-rules/` (see `common/process-overview.md`, `inception/*.md`, `construction/*.md`, `extensions/**`).

When a skill or user points you at a phase, **read that file** before acting. Do not invent alternate workflows.

## Other Cursor rules (always-on context)

- Project facts and stack: `.cursor/rules/project-context.mdc`
- Durable memory: `.cursor/rules/memory.mdc`
- Deep rule path map (optional): `.cursor/rules/aidlc-rule-reference.mdc`

## Generated paths (do not edit by hand)

Regenerate derived Cursor files with:

`./.unicli-rules/sync.sh --fix`

Includes `.cursor/rules/workflow.mdc`, `.cursor/rules/subagent-orchestration.mdc`, `.cursor/skills/**`, `.cursor/agents/**`, MCP JSON, etc.

## Remote workflow gates (Cursor — Jira + GitLab MR)

Canonical procedure: `.unicli-rules/common/jira-integration.md`, `.unicli-rules/templates/remotes/README.md`, and Construction `aidlc-build-and-test` Step 11. Cursor hooks enforce markers; do not call remote MCP until audit/state match the hook contract.

### Jira (`jira_*` MCP)

`beforeMCPExecution` runs `.cursor/hooks/jira_gate_guard.py` (matcher `jira_`). When the current git branch matches an `## AI-DLC … Workstream` section in `aidlc-docs/aidlc-state.md` that lists that branch:

- **`jira_create_issue`**: `aidlc-docs/audit.md` must contain `APPROVAL-JIRA-CREATE: granted [unit={unit}]` for that workstream unit (or `JIRA-WAIVER: approved-by-user [unit={unit}] reason=…`).
- **`jira_transition_issue` / `jira_update_issue`**: state must list a real `**Jira Ticket**: NWAE-###` for the unit, and audit must contain `JIRA-CREATED: {that key} [unit={unit}]` (unless waived as above).

Write markers to `audit.md` **before** invoking Jira MCP.

### GitLab merge request (`gitlab_create_merge_request`)

Same branch → workstream resolution as the Jira guard. Before calling `gitlab_create_merge_request`:

1. User has agreed to open the MR (Y).
2. Append exactly one line to `aidlc-docs/audit.md`: `APPROVAL-MR-CREATE: granted [unit={unit}]` (same `{unit}` as the active workstream).
3. MR **description** must be the stdout of `python3 scripts/render-ai-dlc-remote-templates.py --target gitlab-body --values-file …` per `common/jira-integration.md` §6 (not a hand-written stub).
4. MR **title** must include every Jira key from `**Jira Ticket**` for that unit (space-separated), per `common/jira-integration.md`.
5. After success, append `MR-CREATED: !{iid} [{keys}]` to `aidlc-docs/audit.md`.

`beforeMCPExecution` runs `.cursor/hooks/gitlab_mr_gate_guard.py` (matcher `gitlab_create_merge_request`). It requires, for that unit: `APPROVAL-MR-CREATE: granted [unit={unit}]`, prior `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` in audit, and (unless `JIRA-WAIVER` applies for that unit) a real `**Jira Ticket**: NWAE-###` in state. If no workstream section matches the current branch, the hook does not block (non–AI-DLC branches).

### Task / subagents

Do not delegate `jira_*` or `gitlab_create_merge_request` to a subagent Task unless the main thread has already written the required audit markers and the subagent only performs the MCP call as instructed. Prefer running Jira/MR steps from the main agent while following `aidlc-*` skills.

## Remote workflow gates (Claude Code — identical semantics, different hook wiring)

Claude Code enforces the same Jira and GitLab MR gates via `PreToolUse` hooks in `.claude/settings.json` (generated from `.unicli-rules/claude-hooks.json` by `sync.sh`). The matchers are `mcp__mcp-atlassian__jira_*` and `mcp__gitlab__create_merge_request`. The hook scripts (`jira_gate_guard.py`, `gitlab_mr_gate_guard.py`) are shared between Cursor and Claude Code and normalize the tool name format automatically.

The `workflow_transition_guard.py` PreToolUse hook is also wired on Claude Code (via `.claude/settings.json`) in addition to Cursor (via `.cursor/hooks.json`).

Both CLIs are now **fail-closed** for MCP gate enforcement.

## Build and Test (Cursor — strict gates + codegen feedback)

- Before claiming **Build and Test** complete or writing `GATE-QA: PASS` in `aidlc-docs/audit.md`, read the **entire** `.cursor/skills/aidlc-build-and-test/SKILL.md` and follow Steps 3–7 (and `.unicli-rules/construction/build-and-test.md`).
- **Never** append `GATE-QA: PASS` or `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED` without a **BLOCKING** `qa-tester` **Task** whose invocation is logged in `audit.md` as `SUBAGENT-INVOCATION: qa-tester [unit=u##] task_id=<...> result=PASS|FAIL`. The `workflow_transition_guard` hook enforces this for both Cursor and Claude Code — it blocks checking `[x] Build and Test` if the marker is absent.
  - **Exemption** (wiring-only / non-production changes): If the unit contains no production code changes (e.g. hook wiring, skill/doc updates, sync.sh changes only), record `GATE-WAIVER: qa-tester [unit=u##] reason=<category>` in `aidlc-docs/audit.md` instead. This formally waives the subagent requirement and is auditable. Do NOT use the old free-text `GATE-QA: N/A — …` form; the guard does not accept that as a waiver.
- **Gradle / test evidence**: use `./gradlew clean test` or CI-equivalent on each affected Gradle root; do **not** infer full test re-execution from a log that is only `UP-TO-DATE` for `:test` tasks—force execution with `clean`, explicit `:test`, or `--rerun-tasks` when needed.
- On any **FAIL** gate: write `aidlc-docs/construction/{unit}/build-and-test/fix-request-{unit}.md`, then delegate remediation via **Task** to the correct `codegen-*` agent per `.cursor/rules/subagent-orchestration.mdc` and the Construction guide (max **3** loops). Do not write pass markers until gates are green.

