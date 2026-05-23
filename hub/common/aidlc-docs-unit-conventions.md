# AI-DLC Docs — 유닛 문서화 규약

## 개요

`aidlc-docs/construction/` 아래 각 유닛(Unit of Work)의 설계·산출물은 **유닛 번호 기반 단일 정규 폴더**로 관리한다. 같은 유닛에 대한 결정사항은 반드시 해당 폴더 하나에 집중시켜 SSOT(Single Source of Truth)를 유지한다.

---

## 폴더 명명 규칙

### Canonical 폴더명

```
aidlc-docs/construction/u{NN}-{descriptive-name}/
```

| 유닛 | Canonical 폴더 | 코드 디렉토리 |
|------|--------------|-------------|
| U01 인프라 | `u01-infrastructure/` | `infra/` |
| U01-DB | `u01-db/` | `infra/local-fullstack/postgres-init/` |
| U02 Resource Inventory | `u02-resource-inventory/` | `resource-inventory/` |
| U03 Resource Catalog | `u03-resource-catalog/` | `resource-catalog/` |
| U04 Change Management | `u04-change-management/` | `change-management/` |
| U05 Data Collection | `u05-data-collection/` | `data-collection/` |
| U06 Data Reconciliation | `u06-data-reconciliation/` | `data-reconciliation/` |
| U07 Legacy Integration | `u07-legacy-integration/` | `legacy-integration/` |
| U08 IPAM | `u08-ipam/` | `ipam-service/` |
| U09 Zone Management | `u09-zone-management/` | `zone-management/` |
| U10 Topology | `u10-topology/` | `topology-service/` |
| U11 Frontend | `u11-frontend/` | `frontend/` |
| U13 Tango-I-DB Migration | `u13-tango-i-db-migration/` | `scripts/tango-im/` |
| U14 Legacy Topology Projection | `u14-legacy-topology-projection/` | `resource-inventory/` (Kafka outbox) |
| U15 TMF CTK Runtime | `u15-tmf-ctk-runtime/` | `tools/tmf-ctk/` |
| U16 TMF CTK Integration | `u16-tmf-ctk-integration/` | `tools/tmf-ctk/` + `infra/local-fullstack/` |

> 신규 유닛 추가 시: `u{NN}-{kebab-case-name}/` 형식으로 이 테이블에 추가.

---

## 폴더 내부 표준 구조

```
aidlc-docs/construction/u{NN}-{name}/
├── INDEX.md                    # ← SSOT 진입점 (필수)
├── functional-design/          # 기능 설계
├── nfr-requirements/           # NFR 요구사항
├── nfr-design/                 # NFR 설계
├── infrastructure-design/      # 인프라 설계
├── code/                       # 코드 생성 요약 (마크다운만)
├── build-and-test/             # 빌드/테스트 리포트
└── history/                    # 과거 iteration 백업
    ├── {old-folder-name}/      # git mv로 이동 (git history 보존)
    └── ...
```

**서브피처**: 유닛 내 별도 영역(예: U07의 DMS sync)은 `history/` 가 아닌 `{unit}/sync/` 같은 named 서브폴더로 유지.

---

## INDEX.md — 필수 구조

모든 canonical 폴더에 `INDEX.md`를 작성한다. 이것이 해당 유닛의 **SSOT 진입점**이다.

```markdown
# U{NN} — {Title} SSOT

> **Last Consolidated:** YYYY-MM-DD — 본 일자는 폴더 재구성(reorganization) 시점이며,
> 본문이 코드와 동기화되었음을 보장하지 않음. drift 검증은 후속 PR.
> **Status:** {완료 | 대기 | 작업중} (출처: aidlc-state.md)
> **Code SSOT:** `{repo-relative path}` (~{N} files)
> **TMF Compliance:** {PASS | CONDITIONAL PASS | FAIL — N NC waived | N/A}

## 산출물 (this folder)

{실제 존재하는 하위 폴더/파일만 열거}
- `functional-design/` — 기능 설계
- `build-and-test/` — 빌드/테스트 리포트
- `history/` — 과거 iteration 백업
  - `history/{old-name}/` — {설명}

## Inception 교차참조

{해당 유닛의 실제 inception 파일만 열거 — 존재하지 않으면 섹션 생략}
- `aidlc-docs/inception/requirements/u{NN}-*.md`
- `aidlc-docs/inception/plans/u{NN}-*.md`
- `aidlc-docs/inception/application-design/u{NN}-*.md` (해당 시)

## Drift TODO

- [ ] {구체적 의심 항목} — 후속 PR에서 reconcile
- [ ] {예: API 엔드포인트 수 현행화} — 후속 PR

> Drift 본문 갱신은 별도 PR로 분리.
```

### U11-Frontend 전용 추가 섹션

```markdown
## Cross-cutting Frontend Artifacts (참고만 — 이동 없음)

- `aidlc-docs/construction/u09-zone-management/history/u09a/functional-design/frontend-components.md`
- `aidlc-docs/construction/u14-legacy-topology-projection/functional-design/frontend-components.md`
```

---

## Iteration 변형 처리 (history/ 규칙)

같은 유닛에 여러 차수 폴더가 생긴 경우 (예: `u11`, `u11-iteration`, `u11-iteration-3`):

1. **Canonical 선택 기준: 콘텐츠 완전성** (최신순이 아님)
   ```bash
   for d in aidlc-docs/construction/u11*/; do echo "=== $d"; ls "$d"; done
   ```
   subdir 수와 root .md 파일 수가 가장 많은 폴더를 trunk로 선택.

2. **Canonical 폴더로 rename**:
   ```bash
   git mv aidlc-docs/construction/u11 aidlc-docs/construction/u11-frontend
   ```

3. **나머지는 history/ 로 이동** (`git mv` 사용 — git history 보존):
   ```bash
   mkdir -p aidlc-docs/construction/u11-frontend/history
   git mv aidlc-docs/construction/u11-iteration \
     aidlc-docs/construction/u11-frontend/history/u11-iteration
   ```

> **주의**: `git mv` 대신 일반 `mv`를 쓰면 git history가 끊어진다. 반드시 `git mv`.

---

## inception/ 처리 원칙

`inception/` 디렉토리는 **AI-DLC 워크플로우의 phase-level 구조**를 따르므로 유닛 폴더로 이동하지 않는다.

```
aidlc-docs/inception/
├── requirements/   # u{NN}-*.md 파일들 — 그대로 유지
├── plans/          # u{NN}-execution-plan.md 파일들 — 그대로 유지
├── application-design/  # u{NN}-*.md 파일들 — 그대로 유지
└── reverse-engineering/
```

대신 각 유닛의 `INDEX.md` "Inception 교차참조" 섹션에서 **실제 존재하는 파일**을 링크로 참조.

---

## aidlc-state.md 관리 규칙

### 워크스트림 섹션 순서

워크스트림 섹션(`## AI-DLC ... Workstream (Uxx — ...)`)은 **U01→U17 오름차순**으로 유지한다.

- 같은 유닛의 여러 iteration: 시간순(오래된 것 먼저)
- U-번호 없는 특수 섹션(U-FULLSTACK, U99 등): 번호 유닛 뒤에 추가
- 고정 상단 섹션(`## Project Information`, `## Phase 1 완료 현황`, `## Workspace State`, `## Extension Configuration`, `## Branch Lineage`)은 항상 위치·내용 불변

### 새 유닛 workstream 추가 시

올바른 U-번호 위치에 섹션을 삽입. 맨 끝에 추가하지 않는다.

---

## Relates-To-ADR 메타

모든 유닛의 `INDEX.md`는 상단에 ADR 백링크 메타를 보유한다. ADR이 본 프로젝트의 SSOT이며([`adr-conventions.md`](./adr-conventions.md)), unit 산출물에서 결정 이력으로 진입할 수 있어야 한다.

### 형식

`INDEX.md`의 frontmatter 또는 본문 최상단(헤더 직후)에:

```markdown
**Relates-To-ADR**: [0005](../../adr/cross-cutting/0005-hexagonal-4-module-layout.md), [0006](../../adr/cross-cutting/0006-spring-boot-3.4-baseline.md), [0019](../../adr/microservices/0019-ipam-service-domain-scope.md)
```

규칙:
- 영향이 큰 ADR 위주(보통 2~6건). 모든 ADR을 나열할 필요는 없음.
- 신규/변경 결정 PR에 새 ADR이 포함되면 해당 unit `INDEX.md`도 갱신 필요.
- ADR 카테고리 디렉토리는 상대 경로로 링크.
- 색인 자동 빌드: [`aidlc-docs/index/adr-index.md`](../../aidlc-docs/index/adr-index.md)의 "Affects-Units 역참조" 표가 권위.

### 검증

- 훅 [`hooks/adr_backlink_check.py`](../hooks/adr_backlink_check.py)는 `aidlc-docs/construction/*/INDEX.md`가 변경될 때 `**Relates-To-ADR**` 라인 존재를 검사한다.
- 활성화 여부는 [`extensions/adr/governance/adr-governance.md`](../extensions/adr/governance/adr-governance.md) 참조 — 기본 비활성, opt-in 시 활성.

---

## Drift TODO 원칙

본 PR에서 **폴더 재구성**과 **본문 내용 갱신**을 동시에 하지 않는다.

| 이번 작업 | 다음 작업 |
|----------|---------|
| 폴더 rename, history/, INDEX.md 신설 | INDEX.md의 Drift TODO 항목을 별도 PR에서 해소 |

Drift TODO 항목 예시:
```markdown
- [ ] API 엔드포인트 수: 문서 N개 vs 실제 코드 M개 — 후속 PR
- [ ] 테스트 수 현행화: build-test-report 기준 업데이트 필요
- [ ] 라이브러리 버전: package.json / build.gradle 대조 필요
- [ ] TMF 준수 섹션: specs/tmf/ 최신 리포트와 대조 필요
```

---

## 변경하지 않는 항목

| 항목 | 이유 |
|------|------|
| `aidlc-docs/inception/` 파일 이동 | AI-DLC phase-level 구조 규약 |
| `aidlc-docs/operations/` | 별도 phase; 유닛과 독립 |
| `aidlc-docs/audit.md` | 시계열 감사 로그 — 재정렬 부적합 |
| `aidlc-docs/construction/plans/` | cross-cutting plans, 유닛 비귀속 |
| `aidlc-docs/construction/build-and-test/` | cross-cutting reports, 유닛 비귀속 |
