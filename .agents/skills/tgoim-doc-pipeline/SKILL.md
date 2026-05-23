---
description: >-
  TGO-IM 데이터 모델 문서 파이프라인 — DB 스키마 정의서, IMOWN↔SID 매핑, PG↔SID 매핑을 생성하거나
  갱신할 때 사용합니다. 새 서비스나 IMOWN 테이블 추가, 스크립트 재실행, TMF 속성 감사 노트 작성 시 반드시 이 스킬을 사용합니다.
---

# TGO-IM 데이터 모델 문서 파이프라인

`scripts/tango-im/generate_imown_column_mapping.py` 단일 스크립트가 4가지 문서를 결정론적으로(idempotent) 생성한다. 손으로 문서를 편집하지 않는다 — 항상 스크립트에서 파생한다.

## 사용 시점

- `docs/db/*.md` (PG 테이블 정의서) 를 생성하거나 갱신할 때
- `docs/reports/imown-to-sid-column-mapping.md` (IMOWN↔SID 매핑) 를 갱신할 때
- `docs/reports/postgres-to-sid-column-mapping.md` (PG↔SID 역방향 매핑) 를 갱신할 때
- 새로운 마이크로서비스의 Flyway 마이그레이션이 추가됐을 때
- `pg_field_registry.json` 에 새 TMF 필드 매핑이 추가됐을 때
- IMOWN 허용 테이블 목록이 바뀌었을 때
- TMF 속성 준수 여부를 감사하고 노트를 남길 때

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `scripts/tango-im/generate_imown_column_mapping.py` | 파이프라인 단일 진입점 |
| `scripts/tango-im/pg_field_registry.json` | TMF `target_entity.target_field` → PG `table.column` SSOT |
| `docs/db/` | 서비스별 PG 테이블 정의서 출력 디렉토리 |
| `docs/reports/imown-to-sid-column-mapping.md` | IMOWN↔SID 컬럼 매핑 출력 |
| `docs/reports/postgres-to-sid-column-mapping.md` | PG↔SID 역방향 매핑 출력 |
| `docs/audit/` | TMF 속성 감사 노트 (수동, 1회성) |
| `aidlc-docs/index/code-to-doc-map.md` | 신규 문서 등록 색인 |

## 표준 실행 명령 (전체 재생성)

프로젝트 루트에서 실행:

```bash
python3 scripts/tango-im/generate_imown_column_mapping.py \
  --db-md-out docs/db \
  --db-index-out docs/db/README.md \
  --imown-md docs/reports/imown-to-sid-column-mapping.md \
  --pg-md docs/reports/postgres-to-sid-column-mapping.md
```

두 번 실행해도 `git diff docs/` 출력이 없으면 정상 (idempotency 검증).

## 새 마이크로서비스 PG 스키마 추가

스크립트 내 `ALL_PG_SINKS` 리스트에 튜플을 추가:

```python
# (서비스명, 데이터베이스명, default_schema, Flyway 마이그레이션 디렉토리 Path, TMF registry 포함 여부)
("new-service", "tgoim_newservice", "public",
 REPO_ROOT / "new-service" / "app" / "src" / "main" / "resources" / "db" / "migration",
 False),
```

- Flyway 마이그레이션이 서브디렉토리에 있으면(예: `changemgmt/`) 경로를 해당 서브디렉토리로 지정
- change-management / legacy-integration / data-collection / data-reconciliation은 TMF 페이로드를 transform하지 않으므로 `pg_field_registry.json`에 추가하지 않음

## 새 IMOWN 허용 테이블 추가

스크립트 내 `IMOWN_ALLOWED_TABLES` 리스트에 테이블명 추가:

```python
IMOWN_ALLOWED_TABLES: list[str] = [
    ...
    "im_new_table",  # ImownTables.java whitelist와 동기화
]
```

`ImownTables.java` (`legacy-integration/infrastructure/.../ImownTables.java`) 가 SSOT — 항상 그 파일을 먼저 확인.

## TMF 필드 → PG 컬럼 매핑 추가 (`pg_field_registry.json`)

형식: `서비스` → `entity 이름` → `TMF target_field` → `[PG 테이블, PG 컬럼]`

```json
"new-service": {
  "NewEntity": {
    "tmfFieldName": ["pg_table", "pg_column"]
  }
}
```

최상위에 `"_comment"` 키가 있음 — 서비스 순회 시 `service.startswith("_")` 가드 필수.

## TMF 속성 감사 노트 작성 패턴

`docs/audit/YYYY-MM-DD-<topic>.md` 로 수동 작성. 포함할 내용:

1. **현재 API 버전 확인** — 소스에서 URL prefix 인용 (`@RequestMapping`, `BASE_HREF`, `@PostMapping`)
2. **결론 한 줄** — "v4 컨트랙트 하에서 정상" 또는 "v5 정렬 필요"
3. **코드 인벤토리** — 절대 경로 + 라인번호로 인용
4. **유사 사례** — 다른 서비스의 동일 패턴 점검
5. **마이그레이션 체크리스트** — 후속 unit 범위로 기록 (현 작업에서 코드 변경 없음)

감사 노트는 코드를 변경하지 않는다. 코드 변경이 필요하면 별도 unit으로 분리.

## 문서 생성 후 인덱스 갱신

`aidlc-docs/index/code-to-doc-map.md` 에 신규 문서 backlink 등록:
- "데이터 모델 / 매핑 문서" 섹션에 새 행 추가
- 스크립트 섹션에 새 출력 옵션 반영

## 제약사항

- topology-service는 Neo4j 전용 — PG 스키마 없음, `docs/db/` 출력 없음
- geographic-site-service 와 party-management-service 는 `tgo_im` 데이터베이스를 공유하나 마이그레이션 디렉토리가 분리돼 독립적으로 스캔됨
- HTML 리포트(`docs/imown-sid-load-report.html`) 는 기존 파이프라인이 별도 유지 — `--inject-html` 옵션

