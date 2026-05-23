# Validation Spec — aidlc-workflow

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/aidlc-state.md` exists (if absent, coordinator bootstraps by dispatching `aidlc-workspace-detection`)
- [ ] `aidlc-docs/audit.md` accessible (for gate marker reads)

## Artefact contract

This skill is a **thin coordinator** — it produces no stage artefacts of its own. All artefacts are produced by the dispatched stage skills.

| Artefact path | Required | Validation |
|---|---|---|
| `aidlc-docs/aidlc-state.md` | yes (read) | Contains `## AI-DLC Active Workstream` and `## Extension Configuration` sections |
| `aidlc-docs/audit.md` | yes (read) | Last 40 lines are scanned for gate markers |

## Gate marker contract

This skill **reads** markers; it does **not** emit them. Dispatched stage skills emit their own markers.

### Markers read (approval gate guard — Step 4)

| Dispatch target | Required prior marker in audit.md |
|---|---|
| Any next Inception stage | `APPROVAL-STAGE: {PREV_STAGE}_APPROVED` or `SKIP: {stage-name} — ...` |
| Code Generation Part 2 (codegen subagents) | `APPROVAL-STAGE: CODE_GENERATION_PLAN_APPROVED [unit={unit}]` |
| Build and Test | `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]` |
| Next unit / Operations | `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` |

### Marker format correction

If `{PREV_STAGE}_COMPLETE` (wrong suffix) is found but no `_APPROVED`:
- Coordinator informs user and writes corrected `APPROVAL-STAGE: {PREV_STAGE}_APPROVED [unit={unit}]` on user confirmation.

## Subagent dispatch contract

The coordinator dispatches all stage skills via the **Task tool** (not direct subagents). At least one dispatch must occur per coordinator run.

| Dispatched skill | Condition |
|---|---|
| `aidlc-workspace-detection` | `aidlc-state.md` absent (first run) |
| `aidlc-reverse-engineering` | Brownfield AND no RE artifacts |
| `aidlc-requirements-analysis` | Workspace Detection `[x]` and RA not done |
| `aidlc-user-stories` | RA complete AND Execute-IF criteria met |
| `aidlc-workflow-planning` | After RA (and User Stories if executed) |
| `aidlc-application-design` | Execute-IF criteria met |
| `aidlc-units-generation` | Execute-IF criteria met |
| `aidlc-functional-design` | Per-unit — Execute-IF criteria met |
| `aidlc-nfr-requirements` | Per-unit — Execute-IF criteria met |
| `aidlc-nfr-design` | Per-unit — NFR Requirements was executed |
| `aidlc-infrastructure-design` | Per-unit — Execute-IF criteria met |
| `aidlc-code-generation` | Per-unit — ALWAYS |
| `aidlc-build-and-test` | Per-unit — ALWAYS after Code Generation |
| `aidlc-operations` | All Construction units complete |

**BLOCKING subagents**: None dispatched directly by coordinator — gate blocking is enforced by the coordinator's own guard (Step 4) before dispatch.

**Extension flags**: Coordinator reads `ext_config` and includes relevant flags in each Task prompt. Never writes `ext_config`.

## Failure modes

| Condition | Action |
|---|---|
| `aidlc-state.md` absent | Display welcome banner; dispatch `aidlc-workspace-detection`; return |
| Prior stage marker absent | Re-display 2-option gate for that prior stage; wait for response; log; re-enter Step 3 |
| `{PREV_STAGE}_COMPLETE` found (wrong suffix) | Prompt user to confirm format correction; write corrected marker on yes |
| Required hard-blocker marker absent | Block dispatch; re-display relevant gate; wait |
| Extension `ADR Governance: Enabled` | Include ADR gate reminder in every dispatched Construction skill prompt |
