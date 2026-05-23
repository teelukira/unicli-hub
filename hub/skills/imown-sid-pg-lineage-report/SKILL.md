---
name: imown-sid-pg-lineage-report
description: >-
  IMOWN MySQL → TMF SID ABE → PostgreSQL 3계층 데이터 리니지 리포트를 생성하거나 갱신할 때 사용합니다.
  IMOWN/SID/PG 어느 한 쪽이 변경됐거나 단위 종료 시점에 리포트 갱신이 필요할 때 호출합니다.
---

# IMOWN → SID → PG 3계층 리니지 리포트

`scripts/reports/build_imown_sid_pg_lineage_report.py` 한 줄로 self-contained HTML 리포트를 재생성한다. 손으로 HTML을 편집하지 않는다 — 항상 스크립트에서 파생한다.

## 사용 시점

- IMOWN 컬럼 매핑(`docs/generated/imown-column-mapping-full.json`)이 갱신됐을 때
- PostgreSQL Flyway DDL(각 서비스 `app/src/main/resources/db/migration/V*.sql`)이 변경됐을 때
- 새 SID ABE 매핑이 추가됐을 때
- 단위(Unit) 종료 스냅샷으로 현황 리포트가 필요할 때

## 사전조건

`docs/generated/imown-column-mapping-full.json`이 최신 상태여야 한다. 필요 시 먼저:

```bash
python3 scripts/tango-im/generate_imown_column_mapping.py \
  --db-md-out docs/db \
  --db-index-out docs/db/README.md \
  --imown-md docs/reports/imown-to-sid-column-mapping.md \
  --pg-md docs/reports/postgres-to-sid-column-mapping.md
```

## 실행 명령

프로젝트 루트에서:

```bash
python3 scripts/reports/build_imown_sid_pg_lineage_report.py
```

산출물:
- `docs/reports/imown-sid-pg-lineage.html` — 완전 자기완결형 HTML (외부 자산 없음 — Mermaid JS 인라인 포함)
- `docs/reports/imown-sid-pg-lineage.spec.json` — 디버그용 엔진 스펙

> **최초 실행 시 인터넷 필요**: Mermaid JS를 `scripts/reports/_mermaid@11.4.min.js` 에 다운로드·캐시.
> 이후 빌드는 캐시만 사용 (완전 오프라인 가능). 캐시 파일은 `.gitignore` 처리됨.

브라우저에서 열기:

```bash
open docs/reports/imown-sid-pg-lineage.html
```

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `scripts/reports/build_imown_sid_pg_lineage_report.py` | 리포트 생성기 단일 진입점 |
| `hub/skills/html-report/utils/theme.py` | Mermaid 설정 + CSS 테마, `MERMAID_CDN` / `MERMAID_CACHE` 정의 |
| `hub/skills/html-report/utils/_mermaid@11.4.min.js` | Mermaid JS 로컬 캐시 (gitignored, 최초 실행 시 자동 생성) |
| `docs/generated/imown-column-mapping-full.json` | 입력: 285개 IMOWN→SID→PG 컬럼 매핑 |
| `docs/generated/postgresql-sink-tables.json` | 입력: PG DB별 싱크 서비스 매핑 |
| 각 서비스 `app/.../db/migration/V*.sql` | 입력: Flyway DDL (PG 스키마 상세) |
| `docs/reports/imown-sid-pg-lineage.html` | 출력: 최종 리포트 |
| `hub/skills/html-report/utils/report_engine.py` | Blueprint Dossier 렌더 엔진 (재사용) |

## 리포트 구성

1. **개요 + 통계** — IMOWN 테이블 수, ABE 수, PG 테이블 수, 컬럼 매핑 수, 변환 타입 분포
2. **3계층 리니지 다이어그램** — Mermaid flowchart LR (Priority 10 테이블 중심)
3. **SID ABE 카탈로그** — ABE별 IMOWN→PG 매핑 표
4. **Priority 10 테이블** — U13 Phase 1 핵심 테이블 상세 (펼침 ON)
5. **나머지 35 테이블** — 전체 IMOWN 테이블 상세 (펼침 OFF)
6. **PostgreSQL 스키마 상세** — 6개 마이크로서비스별 erDiagram + 컬럼 표
7. **변환 타입 범례** — DIRECT / EXPRESSION / CODE_LOOKUP / CONSTANT 설명

## 다이어그램 가독성 조정

다이어그램이 작거나 글자가 잘 안 보일 때 조정 포인트:

| 설정 위치 | 항목 | 현재값 |
|-----------|------|--------|
| `theme.py` `MERMAID_INIT` | `fontSize` | `'16px'` |
| `theme.py` `MERMAID_INIT` | `flowchart.nodeSpacing` | `60` |
| `theme.py` `MERMAID_INIT` | `flowchart.rankSpacing` | `90` |
| `theme.py` `MERMAID_INIT` | `flowchart.useMaxWidth` | `false` (축소 금지) |
| `theme.py` CSS | `.mermaid-wrap svg` | `max-width:none!important` (SVG 축소 방지) |
| `build_*.py` `build_er_diagram` | 컬럼 캡 | `16` (테이블당 최대 표시 컬럼 수) |

**3계층 다이어그램 노드 색상**: `build_lineage_mermaid()` 내 `classDef imown/sid/pg` 로 IMOWN(노란색) · SID(파란색) · PG(초록색) 구분.

## 다이어그램 전체화면 / 줌·팬

각 다이어그램 우측 상단의 `⛶` 버튼 클릭 → 전체화면 모달.

| 조작 | 동작 |
|------|------|
| 마우스 휠 | 커서 위치 중심으로 확대/축소 |
| 마우스 드래그 | 팬 |
| 터치 한 손가락 드래그 | 팬 |
| 터치 두 손가락 핀치 | 확대/축소 |
| 툴바 `＋` / `－` | 1.25× / 0.8× 단계 줌 |
| 툴바 `⊡` 또는 `0` | 화면에 맞춤(fit) |
| `ESC` 또는 툴바 `✕` | 닫기 |

**구현 위치**: `theme.py` `MERMAID_ENHANCE_JS` — SVG 자연 크기 픽스 + 모달 + 줌/팬 로직 일체 포함.

**줌 공식** (커서 중심 보존):
```
tx_new = cx - (cx - tx) * (newScale / oldScale)
ty_new = cy - (cy - ty) * (newScale / oldScale)
```

## 새 서비스 PG 스키마 추가

스크립트 내 `PG_SERVICES` 리스트에 튜플 추가:

```python
PG_SERVICES = [
    ...
    ("new-service", "tgoim_newdb", "public",
     REPO_ROOT / "new-service" / "app" / "src" / "main" / "resources" / "db" / "migration"),
]
```

## 수정 시 주의

스크킬 파일 변경 후 파생 디렉토리 동기화:

```bash
./sync.sh --fix
```

`.claude/skills/`, `.codex/`, `.cursor/`, `.kiro/` 에 자동 전파됨.

## 외부 참조

Confluence 03-1-1 마이그레이션 데이터 모델 흐름: 참조 링크만 (MCP fetch 없음).
