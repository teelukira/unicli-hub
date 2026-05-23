---
inclusion: auto
---

# AI-DLC 워크플로우 가이드 (Kiro 적용)

## AI-DLC 3단계 라이프사이클

### INCEPTION (기획) — 완료됨 (리서치 + TMF Knowledge Prep 연동)
- Workspace Detection, Requirements Analysis, Workflow Planning 완료
- 산출물: `aidlc-docs/inception/`
- **리서치 에이전트 활용**: 각 Unit의 INCEPTION 단계에서
  `aidlc-researcher` 서브에이전트를 호출하여 최신 아키텍처/기술 트렌드를 조사한 후 설계에 반영
  - 에이전트: `.kiro/agents/aidlc-researcher.json` (Opus 4.6 모델 + Tavily MCP)
  - 단축키: `Ctrl+Shift+R` 로 직접 전환 가능
  - 서브에이전트 호출 시 `agent_name: "aidlc-researcher"` 지정
- **TMF Knowledge Preparation**: 각 Unit의 INCEPTION 시작 전에
  `tmf-knowledge-ingest` 서브에이전트를 호출하여 해당 Unit에 필요한 TMF/SID/eTOM/ODA 규격을
  `docs/tmf-oracle/`에 미리 파싱·저장 (상세: 아래 "TMF Knowledge Preparation 절차" 참조)

### CONSTRUCTION (구현) — 진행 중
각 Unit별 순차 실행:
1. Functional Design (조건부) — 비즈니스 로직 상세 설계
2. NFR Requirements (조건부) — 비기능 요구사항, 기술 스택 선정
3. NFR Design (조건부) — NFR 패턴 설계
4. Infrastructure Design (조건부) — 인프라 매핑
5. Code Generation (필수) — Part 1: 계획, Part 2: 코드 생성
6. Build and Test (필수) — 빌드/테스트 지침

### OPERATIONS (운영) — 미래 확장용 플레이스홀더

## Unit of Work 목록 (Phase 1)

| Unit | 이름 | 상태 |
|------|------|------|
| U01 | 인프라 Foundation | ✅ 완료 |
| U01-DB | Database Foundation | ✅ 완료 |
| U02 | Resource Inventory Core (TMF639) | ⏳ 다음 |
| U03 | Resource Catalog (TMF634) | 대기 |
| U04 | Change Management (BPM + Camunda) | 대기 |
| U06 | Data Reconciliation Engine | 대기 |
| U07 | Legacy Integration Hub | 대기 |
| U08 | IP Address Management | 대기 |
| U09 | Zone Management | 대기 |
| U10 | Topology Service (Neo4j) | 대기 |
| U11 | Frontend MVP | 대기 |

## 핵심 원칙
- 각 Unit은 완전히 완료(설계+코드) 후 다음 Unit으로 이동
- 모든 단계에서 사용자 승인 필수 (REVIEW REQUIRED)
- audit.md에 모든 상호작용 기록
- aidlc-state.md에 진행 상태 추적
- 코드 생성 시 plan 문서의 체크박스 즉시 업데이트

## TMF Knowledge Preparation 절차

각 Unit의 CONSTRUCTION 시작 전에 반드시 실행하는 선행 단계.
해당 Unit이 의존하는 TMF/SID/eTOM/ODA 규격이 `docs/tmf-oracle/`에 파싱되어 있는지 확인하고,
없으면 `tmf-knowledge-ingest` 에이전트로 파싱한다.

### 실행 흐름

```
Unit 시작
  │
  ▼
[Step 0] TMF Knowledge Preparation
  │
  ├─ 1. 의존성 매트릭스에서 해당 Unit의 필요 규격 확인
  ├─ 2. docs/tmf-oracle/ 에 해당 청크가 존재하는지 검사
  ├─ 3-A. 청크 존재 → "Knowledge Ready" 로그 → Step 1로 진행
  ├─ 3-B. 청크 미존재 → docs/raw/ 에 원본 파일 존재 여부 확인
  │       ├─ 원본 있음 → tmf-knowledge-ingest 호출하여 파싱
  │       └─ 원본 없음 → ⚠️ 사용자에게 부족 자료 안내 (아래 형식)
  └─ 4. 파싱 완료 확인 후 Construction Step 1 진행
```

### 부족 자료 안내 형식

원본 파일이 `docs/raw/`에 없을 경우 아래 형식으로 사용자에게 안내:

```
⚠️ TMF Knowledge Gap 발견

Unit: {unit-id} ({unit-name})
부족한 규격:
  - {규격명} ({파일명 예시})
    → 업로드 경로: docs/raw/{domain}/{파일명}
    → 다운로드: https://www.tmforum.org/resources/{resource-id}

조치: 위 파일을 해당 경로에 업로드한 후 다시 진행해주세요.
```

### Unit별 TMF 의존성 매트릭스

| Unit | OpenAPI | SID | eTOM | ODA |
|------|---------|-----|------|-----|
| U02 Resource Inventory | TMF639 ✅ | resource-domain (physical/logical-resource) | operations/rlm (Resource Lifecycle Mgmt) | IG1171, IG1242 (TMFC639) |
| U03 Resource Catalog | TMF634 | resource-domain (resource-specification) | strategy-infrastructure-product | IG1171, IG1242 (TMFC634) |
| U04 Change Management | TMF641, TMF702 | service-domain, common-domain | operations/slm, e2e-flows | IG1171, IG1242 (TMFC641, TMFC702) |
| U06 Data Reconciliation | TMF642, TMF621 | resource-domain, common-domain | operations/rlm | IG1171, IG1242 (TMFC642, TMFC621) |
| U07 Legacy Integration | TMF639, TMF634 | resource-domain | operations/rlm | GB998 (concepts) |
| U08 IP Address Mgmt | TMF639 | resource-domain (logical-resource) | operations/rlm | — |
| U09 Zone Management | TMF639 | resource-domain, common-domain (location) | operations/rlm | — |
| U10 Topology Service | TMF639 | resource-domain (compound-resource) | operations/rlm | — |
| U11 Frontend MVP | — | — | — | GB998 (concepts) |

### 현재 파싱 상태 (2026-04-09)

| 도메인 | 파싱 완료 | 미파싱 |
|--------|----------|--------|
| openapi | tmf639 (5 chunks) | tmf634, tmf641, tmf642, tmf621, tmf702 |
| sid | — | resource-domain, service-domain, common-domain 전체 |
| etom | — | operations, strategy-infrastructure-product, e2e-flows 전체 |
| oda | — | concepts-principles, component-definition, component-inventory 전체 |

### 호출 예시 (U02 시작 전)

U02는 TMF639 청크가 이미 존재하므로 SID/eTOM/ODA만 파싱 필요:

```json
// SID + eTOM + ODA 병렬 파싱 (서로 독립적)
{
  "task": "U02 TMF Knowledge Preparation — SID/eTOM/ODA 파싱",
  "stages": [
    {
      "name": "sid-resource-domain",
      "role": "tmf-knowledge-ingest",
      "prompt_template": "SID GB922 Excel에서 Resource Domain (PhysicalResource, LogicalResource, CompoundResource, ResourceSpecification) ABE를 파싱해서 docs/tmf-oracle/sid/resource-domain/ 에 저장해줘. 원본: docs/raw/sid/gb922-information-framework-models-suite-v25-0/information-framework-sid-excel-format-v25-0/GB922_Information_Framework_SID_Excel_v25.0.xlsx"
    },
    {
      "name": "etom-rlm",
      "role": "tmf-knowledge-ingest",
      "prompt_template": "eTOM GB921 Resource Process Decompositions에서 Resource Lifecycle Management (RLM) L2/L3 프로세스를 파싱해서 docs/tmf-oracle/etom/operations/ 에 저장해줘. 원본: docs/raw/etom/gb921-business-process-framework-etom-suite-v25-0/gb921-resource-process-decompositions-v24-0/GB921_Resource_Process_Decompositions_v24.0.pdf"
    },
    {
      "name": "oda-components",
      "role": "tmf-knowledge-ingest",
      "prompt_template": "ODA IG1171 Component Definition과 IG1242 Component Inventory에서 TMFC639 관련 내용을 파싱해서 docs/tmf-oracle/oda/ 에 저장해줘. 원본: docs/raw/oda/IG1171_ODA_Component_Definition_v5.0.0.pdf, docs/raw/oda/IG1242_ODA_Component_Inventory_v22.0.0.pdf"
    }
  ]
}
```

## 서브에이전트 가이드

### Code Generation 전문 서브에이전트 (4종)

CONSTRUCTION Phase의 Code Generation 단계에서 Unit 유형에 따라 전문 서브에이전트를 호출합니다.

#### 서브에이전트 매핑 테이블

| 서브에이전트 | 전문 영역 | 단축키 | 적용 Unit |
|-------------|----------|--------|----------|
| `codegen-iac` | Terraform/HCL, AWS 인프라 | `Ctrl+Shift+1` | U01 |
| `codegen-backend` | Java 21 + Spring Boot 3.4.x | `Ctrl+Shift+2` | U02~U10 |
| `codegen-frontend` | React 18 + TypeScript | `Ctrl+Shift+3` | U11 |
| `codegen-db` | Flyway + PostgreSQL + JPA Entity | `Ctrl+Shift+4` | U01-DB, U02~U10 (DB 관련) |

#### Unit별 서브에이전트 호출 매핑

| Unit | 호출 서브에이전트 | 호출 순서 |
|------|-----------------|----------|
| U01 Infrastructure | `codegen-iac` | 단독 |
| U01-DB Database | `codegen-db` | 단독 |
| U02 Resource Inventory | `codegen-db` → `codegen-backend` | DB 먼저, 백엔드 후 |
| U03 Resource Catalog | `codegen-db` → `codegen-backend` | DB 먼저, 백엔드 후 |
| U04 Change Management | `codegen-db` → `codegen-backend` | DB 먼저, 백엔드 후 |
| U06~U10 | `codegen-db` → `codegen-backend` | DB 먼저, 백엔드 후 |
| U11 Frontend MVP | `codegen-frontend` | 단독 |

#### 호출 방법 (Kiro `subagent` 도구)

Code Generation Part 2 (Generation) 에서 각 Step 실행 시 Kiro의 `subagent` 도구를 사용합니다.
`subagent` 도구는 `task`, `stages` 파라미터를 받으며, 각 stage의 `role`에 에이전트명을 지정합니다.

```json
// IaC 코드 생성 (U01) — 단일 stage
{
  "task": "U01 Infrastructure Code Generation Step N",
  "stages": [{
    "name": "codegen-iac-step-n",
    "role": "codegen-iac",
    "prompt_template": "U01 Step N: {step 설명}. infra/ 디렉토리에 코드 생성해줘. 계획: aidlc-docs/construction/plans/u01-code-generation-plan.md 의 Step N 참조"
  }]
}

// Backend 코드 생성 (U02) — 단일 stage
{
  "task": "U02 Resource Inventory Code Generation Step N",
  "stages": [{
    "name": "codegen-backend-step-n",
    "role": "codegen-backend",
    "prompt_template": "U02 Step N: {step 설명}. resource-inventory/ 디렉토리에 코드 생성해줘. 계획: aidlc-docs/construction/plans/u02-code-generation-plan.md 의 Step N 참조"
  }]
}
```

#### 병렬 호출 가능 케이스

동일 Unit 내에서 독립적인 Step은 `stages` 배열에 `depends_on` 없이 나열하면 병렬 실행됩니다:
```json
// U02에서 DB와 Backend를 병렬로 (서로 독립적인 Step인 경우만)
{
  "task": "U02 병렬 코드 생성",
  "stages": [
    {
      "name": "db-migration",
      "role": "codegen-db",
      "prompt_template": "U02 Step 1: Flyway 마이그레이션 생성"
    },
    {
      "name": "domain-entities",
      "role": "codegen-backend",
      "prompt_template": "U02 Step 2: domain 모듈 엔티티 생성"
    }
  ]
}

// DB → Backend 순차 실행 (의존성 있는 경우)
{
  "task": "U02 순차 코드 생성 (DB 의존)",
  "stages": [
    {
      "name": "db-schema",
      "role": "codegen-db",
      "prompt_template": "U02 Step 1: Flyway 마이그레이션 + JPA 엔티티 생성"
    },
    {
      "name": "backend-service",
      "role": "codegen-backend",
      "depends_on": ["db-schema"],
      "prompt_template": "U02 Step 2: DB 스키마 기반 서비스 레이어 구현"
    }
  ]
}
```

**주의**: DB 스키마에 의존하는 JPA 엔티티는 반드시 `depends_on`으로 `codegen-db` 완료 후 `codegen-backend` 호출

### 1. aidlc-researcher (리서치 에이전트)
- 설정: `.kiro/agents/aidlc-researcher.json`
- 모델: Claude Opus 4.6
- MCP: Tavily (웹 검색)
- 단축키: `Ctrl+Shift+R`
- 결과 저장: `research/{unit-id}-{topic-slug}.md`

#### 자동 호출 시점
1. **Requirements Analysis** — 최신 기술 스택 조사
2. **Application Design** — 아키텍처 패턴/사례 조사
3. **Workflow Planning** — 기술적 리스크/트렌드 조사
4. **NFR Requirements** — 벤치마크/모범사례 조사
5. **NFR Design** — 최신 패턴/라이브러리 조사

#### 호출 방법 (Kiro `subagent` 도구)
```json
{
  "task": "기술 리서치: {조사 주제}",
  "stages": [{
    "name": "research",
    "role": "aidlc-researcher",
    "prompt_template": "{조사할 내용}. 현재 컨텍스트: {Unit/단계}"
  }]
}
```

#### 수동 전환
- `Ctrl+Shift+R` 또는 `/agent aidlc-researcher`
- 복귀: `/agent kiro_default`

### 2. tmf-knowledge-ingest (TMF 규격 변환 에이전트)
- 설정: `.kiro/agents/tmf-knowledge-ingest.json`
- 모델: Claude Opus 4.6
- 단축키: `Ctrl+Shift+I`
- 입력: `docs/raw/` (PDF, Excel, UML 바이너리)
- 출력: `docs/tmf-oracle/` (규격단위 .md 청크)

#### 역할
- `docs/raw/` 의 TMF 바이너리 파일(PDF/Excel)을 파싱
- `docs/tmf-oracle/` 에 규격단위로 구조화된 .md 청크 생성
- 각 청크는 ~200줄, YAML frontmatter + cross_refs 포함

#### 호출 방법 (Kiro `subagent` 도구)
```json
{
  "task": "TMF Knowledge Ingest: TMF639 파싱",
  "stages": [{
    "name": "ingest-tmf639",
    "role": "tmf-knowledge-ingest",
    "prompt_template": "TMF639 PDF를 파싱해서 tmf-oracle/openapi/tmf639/ 에 저장해줘. 원본: docs/raw/openapi/TMF639_*.pdf"
  }]
}
```

#### 수동 전환
- `Ctrl+Shift+I` 또는 `/agent tmf-knowledge-ingest`
- 복귀: `/agent kiro_default`

## AI-DLC 룰 파일 참조
상세 룰은 `hub/` 디렉토리 참조:
- `common/` — 공통 룰 (프로세스, 세션 연속성, 콘텐츠 검증)
- `inception/` — 기획 단계 룰
- `construction/` — 구현 단계 룰 (functional-design, nfr, code-generation 등)
- `extensions/` — 확장 (보안, 테스팅)

### 3. qa-tester (독립 QA 에이전트)
- 설정: `.kiro/agents/qa-tester.json`
- 모델: Claude Sonnet 4
- 단축키: `Ctrl+Shift+5`
- 역할: 코드 생성 에이전트와 **완전 분리**된 독립 QA (긍정 편향 방지)

#### 핵심 원칙: Anti-Bias Independence
- 코드를 "처음 보는 눈"으로 검증 (코드 생성에 관여하지 않음)
- 테스트 통과를 위해 테스트를 수정하지 않음 (코드를 수정해야 함)
- 실패한 테스트를 @Disabled/@Ignore하지 않음
- 커버리지 미달 시 codegen에 추가 테스트 요청

#### 역할
1. 빌드 실행 (Gradle, Terraform validate/plan)
2. 테스트 실행 (JUnit, Testcontainers, REST Assured, jqwik PBT)
3. 결과 분석 (성공/실패 분류, 커버리지 측정)
4. 실패 원인 진단 (스택트레이스 분석, 의존성 문제 식별)
5. 수정 요청서 작성 → 해당 codegen 에이전트에 위임

#### 호출 방법 (Kiro `subagent` 도구)
```json
{
  "task": "U02 resource-inventory 빌드 및 전체 테스트",
  "stages": [{
    "name": "qa-build-test",
    "role": "qa-tester",
    "prompt_template": "U02 resource-inventory 빌드 및 전체 테스트 실행해줘. 계획: aidlc-docs/construction/plans/u02-code-generation-plan.md"
  }]
}
```

### 4. tmf-compliance-reviewer (TMF 표준 준수 검증 에이전트)
- 설정: `.kiro/agents/tmf-compliance-reviewer.json`
- 모델: Claude Sonnet 4
- 단축키: `Ctrl+Shift+6`
- 역할: TMF-10 규칙에 따른 독립 표준 준수 검증

#### 역할
- TMF-01~TMF-09 전체 규칙을 코드 대비 검증
- TMF Oracle 청크(`docs/tmf-oracle/`)를 참조하여 스펙 근거 제시
- `specs/tmf/{unit}/review-report.md` 에 PASS/FAIL verdict 생성
- FAIL 시 blocking findings 목록과 수정 담당 codegen 에이전트 지정

#### 호출 방법 (Kiro `subagent` 도구)
```json
{
  "task": "U02 TMF639 준수 검증",
  "stages": [{
    "name": "tmf-review",
    "role": "tmf-compliance-reviewer",
    "prompt_template": "U02 resource-inventory의 TMF639 준수 여부 검증해줘. TMF Oracle: docs/tmf-oracle/openapi/tmf639/, 소스: resource-inventory/"
  }]
}
```

### 5. web-integration-tester (웹 통합 테스트 에이전트)
- 설정: `.kiro/agents/web-integration-tester.json`
- 모델: Claude Sonnet 4
- 단축키: `Ctrl+Shift+7`
- 역할: 프론트엔드↔백엔드 연동 검증 (API 스키마 + Playwright E2E)

#### 역할
1. API 스키마 검증 — 백엔드 응답 필드와 프론트엔드 TypeScript 타입 일치 확인
2. 로컬 E2E — Playwright로 로컬 환경(local-fullstack + Vite dev) 브라우저 테스트

#### 호출 방법 (Kiro `subagent` 도구)
```json
{
  "task": "웹 통합 테스트 실행",
  "stages": [{
    "name": "web-integration",
    "role": "web-integration-tester",
    "prompt_template": "로컬 환경에서 전체 웹 통합 테스트 실행해줘. E2E: frontend/e2e/, 스키마 검증: scripts/verify-api-schema.sh"
  }]
}
```

### Build and Test 단계 서브에이전트 호출 흐름

```
Code Generation 완료 (모든 Unit)
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│  병렬 실행 (3종 독립 에이전트)                              │
│                                                          │
│  qa-tester          tmf-compliance-reviewer   web-integration-tester │
│  (빌드+단위테스트)    (TMF 스펙 검증)           (API 스키마 + E2E)     │
│                                                          │
│  ├─ PASS             ├─ PASS                  ├─ PASS              │
│  └─ FAIL → fix-req   └─ FAIL → fix-req        └─ FAIL → web-fix-req│
│     → codegen 수정      → codegen 수정           → codegen 수정      │
│     → 재검증 (3회)       → 재검증                  → 재검증 (3회)      │
└──────────────────────────────────────────────────────────┘
  │
  ▼
[Complete] 전체 PASS → Build and Test 단계 완료
```

#### 병렬 호출 가능
3종 에이전트 모두 독립적이므로 `stages` 배열에 `depends_on` 없이 나열하면 병렬 실행됩니다:
```json
{
  "task": "U02 Build & Test — QA + TMF + Web Integration 병렬 검증",
  "stages": [
    {
      "name": "qa-test",
      "role": "qa-tester",
      "prompt_template": "U02 resource-inventory 빌드 및 전체 테스트 실행해줘. JAVA_HOME=/opt/homebrew/Cellar/openjdk@21/21.0.10/libexec/openjdk.jdk/Contents/Home, DOCKER_HOST=unix://$HOME/.colima/default/docker.sock"
    },
    {
      "name": "tmf-review",
      "role": "tmf-compliance-reviewer",
      "prompt_template": "U02 resource-inventory의 TMF639 준수 여부 검증해줘. TMF Oracle: docs/tmf-oracle/openapi/tmf639/, 소스: resource-inventory/, 스펙: specs/tmf/u02/"
    },
    {
      "name": "web-test",
      "role": "web-integration-tester",
      "prompt_template": "로컬 웹 통합 테스트 실행해줘. E2E: frontend/e2e/"
    }
  ]
}
```
