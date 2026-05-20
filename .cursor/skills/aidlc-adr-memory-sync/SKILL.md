---
name: aidlc-adr-memory-sync
description: >-
  When ADR files under `aidlc-docs/adr/` are added or modified — or when a
  PostToolUse hook emits a nudge starting with `adr-memory-sync:` — ALWAYS use
  this skill immediately. Also trigger when the user says "refresh ADR memory",
  "sync serena memory for ADR", "update ADR catalog", or asks why Serena memory
  is out of date with the ADRs. This skill reads the ADR files and updates
  `.serena/memories/adr/catalog.md` (incremental) and per-ADR detail memos for
  Accepted ADRs. READ-ONLY on ADR files — does not edit ADRs, adr-curator does.
  Never edits `aidlc-docs/index/adr-index.md` to avoid hook re-triggering.
allowed-tools:
  - Read
  - Glob
  - Grep
  - mcp__serena__list_memories
  - mcp__serena__read_memory
  - mcp__serena__write_memory
  - mcp__serena__edit_memory
---

# aidlc-adr-memory-sync

ADR 파일을 읽어 Serena memory(`adr/catalog` + per-ADR memos)를 **증분 업데이트**한다.
ADR 파일 자체는 절대 편집하지 않음. ADR 작성/수정은 `adr-curator` 에이전트 담당.

---

## 1. ADR 파일 수집

Glob `aidlc-docs/adr/**/*.md`, 다음 제외:
- `0000-template.md`
- `README.md`

각 파일에서 파싱:
- **ID**: 파일명 앞 4자리 숫자 (e.g., `0007`)
- **slug**: 파일명에서 `NNNN-` 제거, `.md` 제거
- **Title**: `# NNNN.` 로 시작하는 첫 줄에서 제목 부분
- **Frontmatter** (파일 상단 `---` 블록 또는 colon-separated 행):
  - `Date:`, `Status:`, `Affects-Units:`, `Affects-Code:`, `Supersedes:`, `Superseded-By:`
- **Decision 요약**: `## Decision` 섹션의 첫 단락 (최대 3문장)

## 2. 현재 catalog 읽기

`mcp__serena__read_memory` → memory name `adr/catalog`

catalog.md의 테이블 파싱: `| ID | Category | Title | Status | Affects-Units |` 형태.
없으면 신규 생성으로 처리.

## 3. 증분 diff

새로 파싱한 ADR 목록과 catalog 비교:
- **신규** (catalog에 없는 ID): row 추가
- **Status 변경** (특히 `Superseded by NNNN`): row 업데이트
- **그 외 변경** (Title 수정, Affects-Units 변경): row 업데이트
- **변경 없음**: skip (노이즈 방지)

## 4. catalog.md 패치

변경이 있는 경우만 `mcp__serena__write_memory`로 전체 catalog.md를 업데이트.

catalog.md 포맷:
```markdown
# ADR Catalog

> Auto-synced by aidlc-adr-memory-sync skill. Source: aidlc-docs/adr/

## Cross-Cutting

| ID | Title | Status | Affects-Units | File |
|----|-------|--------|---------------|------|
| 0002 | ... | Accepted | U02, U03 | [link](../../aidlc-docs/adr/cross-cutting/0002-...) |

## Frontend
...
## Infrastructure
...
## Microservices
...
## TMF Compliance
...

## Last Updated
{ISO date} — updated: N, added: N, superseded: N
```

카테고리는 디렉토리명 기준: `cross-cutting`, `frontend`, `infrastructure`, `microservices`, `tmf-compliance`.

## 5. per-ADR memo 생성/업데이트

**대상**: `Status`가 `Accepted` 또는 `Accepted (Retroactive)` 인 ADR만.
(`Proposed`, `Deprecated`, `Superseded by NNNN` 은 per-ADR memo 생략)

memo name: `adr/NNNN-slug` (예: `adr/0005-hexagonal-4-module-layout`)

memo 포맷:
```markdown
# ADR NNNN — {Title}

**Status**: {Status}
**Date**: {Date}
**Affects-Units**: {Affects-Units}
**Affects-Code**: {Affects-Code}
**Source**: aidlc-docs/adr/{category}/NNNN-slug.md

## Decision
{Decision 섹션 첫 단락 — 최대 3문장}

## Why
{Consequences > Positive 첫 bullet 또는 Context 마지막 문장}
```

기존 memo가 있으면 `mcp__serena__write_memory` 로 덮어쓰기 (edit_memory 대신 write로 전체 교체).

## 6. 완료 보고

```
aidlc-adr-memory-sync 완료:
  added: N, updated: N, superseded: N, skipped: N
  per-ADR memos: created N, updated N
```

변경이 없으면 "모든 ADR memory가 최신 상태입니다." 로 종료.

---

## 주의사항

- `aidlc-docs/adr/` 파일은 절대 편집 안 함 (Read/Glob/Grep만 사용)
- `aidlc-docs/index/adr-index.md` 도 건드리지 않음 (PostToolUse hook 재발화 방지)
- write_memory는 MCP 도구 → Edit/Write matcher에 걸리지 않아 무한 루프 없음
- Superseded ADR은 catalog의 Status만 `Superseded by NNNN` 으로 표시; per-ADR memo 삭제 불필요

