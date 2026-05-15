# ADR Governance Rules

## Overview

This extension defines the **enforcement** rules for the ADR-based SSOT model defined in [`common/adr-conventions.md`](../../../common/adr-conventions.md). When this extension is enabled in **Full** mode, the rules below become blocking constraints at AI-DLC stages, hooks, and CI.

**Loading**: Loaded only when user opts in via the prompt in `adr-governance.opt-in.md`. Mode (Full/Manual/Disabled) tracked in `aidlc-docs/aidlc-state.md` `## Extension Configuration`.

## Rule ADR-01: Architecture Decision MUST Have an ADR

**Rule**: Whenever an AI-DLC stage produces a decision matching any criterion in [`common/adr-conventions.md` §"ADR 작성 트리거"](../../../common/adr-conventions.md), an ADR file MUST be created in `aidlc-docs/adr/{category}/NNNN-slug.md`.

**Verification**:
- The stage completion message MUST cite the ADR number (e.g., "Created ADR-0042 for new dependency baseline").
- For Full mode, missing ADR is a **blocking finding**.
- For Manual mode, missing ADR triggers an advisory note in the completion message (non-blocking).

**Audit**: Log to `aidlc-docs/audit.md` with rule ID `ADR-01` and stage context.

## Rule ADR-02: ADR Metadata Completeness

**Rule**: Every ADR file under `aidlc-docs/adr/[0-9]*.md` MUST contain the required Nygard-style metadata fields specified in [`common/adr-conventions.md`](../../../common/adr-conventions.md):

- `**Date**: YYYY-MM-DD`
- `**Status**: ...`
- `**Affects-Units**: ...`
- `**Source-Evidence**: ...`

**Verification**:
- `scripts/verify-adr-integrity.sh` (Phase 6 활성화 후) grep-검증:
  ```bash
  find aidlc-docs/adr -name "[0-9]*.md" | while read f; do
    for field in "Date" "Status" "Affects-Units" "Source-Evidence"; do
      grep -q "^- \*\*${field}\*\*:" "$f" || echo "MISSING ${field}: $f"
    done
  done
  ```
- Empty output = PASS. Any MISSING line = blocking finding.

## Rule ADR-03: Unit INDEX MUST Have Relates-To-ADR Backlink

**Rule**: Every `aidlc-docs/construction/{unit}/INDEX.md` MUST contain a `**Relates-To-ADR**:` line listing the ADRs relevant to that unit.

**Verification**:
- `hooks/adr_backlink_check.py` (PostToolUse, Phase 6 활성화 후) runs after any edit to `aidlc-docs/construction/*/INDEX.md` and fails if `Relates-To-ADR` is missing.
- `scripts/verify-adr-integrity.sh` grep-검증:
  ```bash
  find aidlc-docs/construction -name "INDEX.md" | xargs grep -L "Relates-To-ADR:"
  ```
- Empty output = PASS.

## Rule ADR-04: Supersede Chain Integrity

**Rule**: When a new ADR supersedes an existing one:
1. New ADR has `**Supersedes**: NNNN` in its metadata.
2. Old ADR's `**Status**` is updated to `Superseded by NNNN` AND old ADR has `**Superseded-By**: NNNN` added.
3. The old ADR's body is NOT deleted or substantially modified (git history captures change context, but the immutable artifact remains).

**Verification**:
- For every `**Superseded-By**: NNNN` in any ADR, the matching ADR NNNN must exist and contain `**Supersedes**: <originating-number>`.

## Rule ADR-05: PR/MR References ADR for Architecture Changes

**Rule**: When a Merge Request (GitLab) or Pull Request (GitHub) includes changes that match the ADR trigger criteria, the MR/PR description MUST cite the ADR number.

**Verification**:
- MR 템플릿 `.gitlab/merge_request_templates/default.md`(Phase 6 활성화 후)에 필수 **관련 ADR** 섹션이 포함되어야 한다.
- CI 작업은 `aidlc-docs/adr/`를 변경한 MR의 설명에 `관련 ADR`(또는 `Related ADR`) 및 ADR 번호 언급이 없으면 거절한다 [추측 — Phase 6에서 구현].

## Rule ADR-06: Legacy-ID Preservation

**Rule**: ADRs migrated from prior locations (e.g., `specs/tmf/u13c/ADR-U13c-001`) MUST preserve their previous identifier as `**Legacy-ID**: <original-id>` for grep-traceability.

**Verification**:
- Grep `**Legacy-ID**:` in `aidlc-docs/adr/` → expected matches for known historical IDs.
- See [`aidlc-docs/index/adr-index.md` Legacy-ID 역참조](../../../aidlc-docs/index/adr-index.md#legacy-id-역참조).

## Activation Procedure (Phase 6 Reference)

When migrating from Manual to Full mode:

1. Enable in `aidlc-docs/aidlc-state.md` `## Extension Configuration`:
   ```markdown
   - ADR Governance: ✅ Enabled (Full)
   ```
2. Symlink or copy `hooks/adr_backlink_check.py` to `.claude/hooks/` and add PostToolUse entry to `.claude/settings.local.json`.
3. Move MR template draft from `aidlc-docs/operations/adr-automation/merge-request-template-draft.md` to `.gitlab/merge_request_templates/default.md`.
4. Move CI script draft from `aidlc-docs/operations/adr-automation/verify-adr-integrity.sh` to `scripts/verify-adr-integrity.sh` and wire into pre-commit + GitLab CI `.gitlab-ci.yml`.
5. Run `./.unicli-rules/sync.sh --fix` to propagate.
6. Run `scripts/verify-adr-integrity.sh` once to surface existing drift; fix as needed.

## Skip Conditions (N/A)

- Project does not adopt ADR (Disabled mode) → all rules N/A.
- Project in early bootstrap (no decisions yet) → rules N/A until first ADR exists.
