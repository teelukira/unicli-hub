# Validation Spec — aidlc-adr-memory-sync

## Preconditions (machine-checkable)

- [ ] `aidlc-docs/adr/` directory exists and contains at least one `.md` file (excluding `0000-template.md` and `README.md`)
- [ ] Serena MCP tools (`mcp__serena__read_memory`, `mcp__serena__write_memory`) are accessible

**Trigger conditions** (any one sufficient):
- ADR file under `aidlc-docs/adr/` was added or modified
- PostToolUse hook emits nudge starting with `adr-memory-sync:`
- User says "refresh ADR memory", "sync serena memory for ADR", "update ADR catalog", or asks why Serena memory is out of date

## Artefact contract

This skill writes to **Serena memory only** — it does NOT modify any files in the repository.

| Artefact | Required | Validation |
|---|---|---|
| Serena memory: `adr/catalog` | yes (written via `mcp__serena__write_memory`) | Must be a markdown table with columns `ID \| Title \| Status \| Affects-Units \| File`, grouped by category (`cross-cutting`, `frontend`, `infrastructure`, `microservices`, `tmf-compliance`). Must include `## Last Updated` line with ISO date and change counts. |
| Serena memory: `adr/NNNN-slug` (one per Accepted ADR) | yes for each Accepted/Accepted (Retroactive) ADR | Each memo must contain: `**Status**:`, `**Date**:`, `**Affects-Units**:`, `**Affects-Code**:`, `**Source**:`, `## Decision` (first paragraph, max 3 sentences), `## Why` (first positive consequence or context last sentence) |

**Read-only constraint**: `aidlc-docs/adr/` files must NEVER be modified (Read/Glob/Grep only).
**Excluded from writes**: `aidlc-docs/index/adr-index.md` must NOT be touched (prevents PostToolUse hook re-triggering).

**Incremental diff**: Only ADRs with changes (new, status change, title/Affects-Units change) are written. Unchanged ADRs are skipped.

## Gate marker contract

- **No `APPROVAL-STAGE` marker is emitted.** This is a cross-cutting automated skill with no human approval gate.
- Expected pre-marker: none (triggered by hook or user command, not by stage progression)
- Completion is reported inline (not to audit.md): `aidlc-adr-memory-sync 완료: added: N, updated: N, superseded: N, skipped: N; per-ADR memos: created N, updated N`
- If no changes: report "모든 ADR memory가 최신 상태입니다."

## Subagent dispatch contract

- **BLOCKING subagents**: none
- **Conditional subagents**: none

This skill is itself invoked as part of the `adr-curator` and `adr-impact-scanner` subagent workflows, but does not dispatch subagents of its own.

## Failure modes

| Condition | Action |
|---|---|
| `aidlc-docs/adr/` is empty or inaccessible | Report "No ADR files found"; exit without writing |
| Serena MCP tools unavailable | Report error; do NOT attempt file-based fallback; halt |
| ADR file has malformed frontmatter (no `Status:` line) | Skip that ADR; log "skipped (malformed frontmatter: NNNN-slug)"; continue with remaining ADRs |
| `adr/catalog` Serena memory does not exist | Treat as new catalog; write fresh catalog from all parsed ADRs |
| `Proposed` or `Superseded by NNNN` ADR encountered | Update catalog row only; do NOT create or update per-ADR memo for that ADR |
