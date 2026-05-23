# Backlog Writeback Rules

## Defect ID convention

```
QA-<YYYYMMDD>-<HHMM>-<N>
```

Examples: `QA-20260521-1430-1`, `QA-20260521-1430-2`

The sweep ID (`QA-SWEEP-<YYYYMMDD>-<HHMM>`) is the parent; individual defects get sequential `<N>` suffix.

## Append location in backlog.md

Insert the new sweep section **above** `## 🟢 Low / Cosmetic` and **below** any existing `## 🟡` sweep sections. Never reorder or delete existing sections.

## Section template

```markdown
## 🟡 QA Sweep QA-SWEEP-<YYYYMMDD>-<HHMM> — <YYYY-MM-DD>

**Scope**: <mode> | **Healthy containers**: <X>/18 | **Duration**: <Xm Xs>
**Evidence**:
- UI: `docs/todos/qa-screenshots/QA-SWEEP-<id>/`
- CTK: `scripts/tmf-ctk/reports/<UTC>/`
- API: `specs/tmf/api-contract/<UTC>/summary.md`
- SID: `specs/tmf/sid-schema/report-<UTC>.md`
- Research: `docs/research/qa-sweep-<id>-*.md`

| ID | 우선순위 | 내용 | 상태 |
|----|---------|------|------|
| **QA-<id>-1** | P1 | <description> — <evidence path> | open |
| **QA-<id>-2** | P2 | <description> — <evidence path> | open |
```

## Priority taxonomy

| Priority | Label | Criteria |
|----------|-------|----------|
| P1 | 🔴 | Page/API returns 5xx; CRUD broken; CTK unit >5% below threshold; SID mandatory attribute missing |
| P2 | 🟡 | Spec diff; CTK marginal miss; SID type mismatch; UI field missing/wrong |
| P3 | 🟢 | Lint warning; naming drift; cosmetic enum casing; optional SID attribute |
| — | ✅ | All gates PASS — use `done` status on single-row OK entry |

## Status vocabulary (matches existing backlog.md)

- `open` — newly discovered, not yet acted on
- `in progress` — someone is working on it
- `done` — fix merged
- `deferred` — external dependency / out of scope this sprint

## Rules

1. Use Korean descriptions where the content involves Korean domain terms (zone types, KPI names). English is fine for technical defects (HTTP status, schema fields).
2. Do NOT edit or delete existing rows; only append new rows and new sections.
3. Always include the evidence path in the description so future readers can locate the raw report without re-running.
4. Jira keys (`NWAE-###`) are optional — add only when a ticket already exists. Do not create Jira tickets from this skill.
5. After appending to `backlog.md`, add/update the index row in `docs/todos/README.md`:
   ```markdown
   | 🟡 QA Sweep | [backlog.md#qa-sweep-<id>](./backlog.md#qa-sweep-qasweep-yyyymmdd-hhmm) | <Scope> QA sweep — <date> |
   ```
