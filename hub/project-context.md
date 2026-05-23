# TGO-IM OSS Inventory Management — AI-DLC Project

## Project Context

**프로젝트명**: SKT ATOM TGO-IM (Tango Inventory Management) — OSS Inventory Management System 신규 개발

**목표**: 130여 개 레거시 OSS 시스템을 60개로 통합하는 디지털 전환 프로그램 중 인벤토리 관리 도메인 담당. TM Forum ODA/eTOM/SID/TMF Open API 표준 기반 마이크로서비스 아키텍처로 재개발.

**개발 방식**: AI-DLC (AI-Driven Development Lifecycle) — AI Powered Execution with Human Oversight

---

## Quick Reference: Unit of Work (Phase 1 범위)

| Unit | 이름 | AI 커버리지 | 핵심 인간 개입 | 상태 |
|------|------|-------------|----------------|------|
| U01 | 인프라 Foundation (Kong/Kafka/Keycloak/Camunda 8) | 70% | EKS 사이징, 보안 정책 | ✅ 완료 |
| U01-DB | Database Foundation (PostgreSQL/TimescaleDB) | 75% | 스키마 분리 정책, 파티셔닝 전략 | ✅ 완료 |
| U02 | Resource Inventory Core (TMF639) | 80% | SID SKT 확장 속성 선별 | ✅ 완료 (TMF PASS) |
| U03 | Resource Catalog (TMF634) | 85% | 카탈로그 초기 데이터 | ✅ 완료 (TMF **PASS** (run-06)) |
| U04 | Change Management (BPM + Camunda) | 60% | 보상 트랜잭션, 부분 성공 정책 | ✅ 완료 (TMF **PASS** (run-02)) |
| U05 | Data Collection Pipeline (FTP + 50+ 벤더 파서) | 40% | **벤더별 파서 로직 (반드시 인간 검증)** | ✅ 완료 (QA PASS 27/27, TMF PASS) |
| U06 | Data Reconciliation Engine (DR 7단계) | 55% | DR 정책, 자동화 임계값 | ✅ 완료 (QA PASS 41/41) |
| U07 | Legacy Integration Hub (TIO/iSigma/CMS Bus) | 35% | **바이너리 프로토콜 오프셋 검증 필수** | ✅ 완료 (TMF **PASS** (run-04)) |
| U08 | IP Address Management | 75% | CIDR 할당 정책 | ✅ 완료 (TMF PASS) |
| U09 | Zone Management (16종 Zone) | 70% | Zone 비즈니스 룰 | ✅ 완료 (TMF **PASS** (U09-Redo, 6/6 NC 해소)) |
| U10 | Topology Service (Neo4j) | 50% | 그래프 관계 정의 | ✅ 완료 (TMF **PASS** (run-04)) |
| U11 | Frontend MVP (React 18 + ATOM DS) | 75% | SKT ATOM Design System UX | ✅ 완료 |
| U12 | Auth Governance (Keycloak + RBAC) | 80% | 역할별 권한 매트릭스 | ⏸ 대기 |
| U13 | Tango-I-DB Legacy Migration | 65% | **IMOWN 9 테이블 매핑 인간 검증 필수**, OID 정합성 확인 | ✅ 완료 (QA PASS, TMF PASS) |
| U14 | Legacy Topology Projection | 70% | RI Canonical Kafka Outbox, 그래프 관계 정의 | ✅ 완료 (QA PASS, TMF PASS) |
| U15 | TM Forum CTK Runtime Conformance | 75% | Docker/Newman orchestration 검증 | ✅ 완료 |
| U16 | TMF CTK ↔ Local Docker Stack Integration | 80% | CTK matrix 실행 환경, DNS 통합 | ✅ 완료 |
| U24 | TMF NC Remediation (W-3/W-4/W1/W2 4건 해소) | 90% | — | ✅ 완료 (TMF CONDITIONAL PASS) |

> **실시간 상태는 [`aidlc-docs/aidlc-state.md`](aidlc-docs/aidlc-state.md)가 단일 진실 공급원 (single source of truth).** 본 테이블의 상태 컬럼은 스냅샷이며 동기화 지연이 있을 수 있음.

---

## Current Progress (2026-05-13 스냅샷)

- **Inception Phase**: 전체 완료 (User Stories는 skip — API 백엔드 중심, 기획서 기능 정의로 충분)
- **Construction Phase (완료)**: U01 / U01-DB / U02 / U03 / U04 / U05 / U06 / U07 / U08 / U09 / U10 / U11 / U11-Iteration / U13 / U14 / U15 / U16 전체 코드 생성 및 `main` 병합 완료
- **U24 TMF NC Remediation**: ✅ BT 완료, MR 준비 중 — W-3(GeographicSubAddress), W-4(ProfileGuard), W1(OrganizationStatus), W2(Hub/Outbox). **활성 TMF NC waive 0건 (specs/tmf/_summary.md run-07)**.
- **U99 TMF Re-verification**: ✅ 모든 unit PASS (U03/U04/U07/U09/U10 재검증 완료)
- **로컬 Docker 풀스택**: ✅ 완료 (`infra/local-fullstack/` — Colima + 16 컨테이너 원터치, IMOWN 실 데이터 123,614건)
- **idcube-dev 데모 배포**: ✅ 완료 (EC2 + docker-compose, `infra/tgo-dev-demo/` Terraform, OA CIDR 제한)
- **다음 대기 단위**: U12 (Security Baseline Extension 활성화 후 착수) — U24 MR 병합 후 착수
- **Extension 설정** (aidlc-docs/aidlc-state.md의 Extension Configuration 기준):
  - Property-Based Testing: ✅ Enabled (Full)
  - TMF Compliance: ✅ Enabled (Full)
  - Security Baseline: ❌ Disabled (U12 착수 시 활성화 예정)

---

## 핵심 기술 스택

- Backend: Java 21, Spring Boot 3.4.x, Virtual Threads
- Frontend: React 18, TypeScript, Vite, TanStack Router/Query
- API 표준: TMF639 (Resource Inventory), TMF634 (Resource Catalog)
- DB: PostgreSQL 16 (prod), Neo4j (Topology)
- Infra (prod): AWS EKS, Terraform, Kong, Kafka, Keycloak
- CI/CD: pre-commit (google-java-format, Checkstyle, ESLint, Prettier)
- 테스트: JUnit 5, Testcontainers, REST Assured, jqwik PBT, Vitest, Playwright

---

## 아키텍처 패턴

- Hexagonal Architecture (Port Adapter): domain/ → api/ → infrastructure/ → app/
- 각 마이크로서비스는 4개 Gradle 서브모듈로 구성
  - `domain/` — 순수 도메인 (Port, Service, Model, Exception)
  - `api/` — REST Controller, DTO, Mapper
  - `infrastructure/` — JPA Entity, Repository Adapter, Kafka, Feign, Redis
  - `app/` — Spring Boot 조립, Flyway Migration, Config

---

## Design Artifacts Location

기획서 산출물은 `aidlc-docs/inception/business-inputs/`에 있음 (2026-05-12에 `docs/`에서 이동, [ADR Phase 6 정합성]). AI-DLC Inception 단계에서 이 문서들을 참조:

| 파일 (`aidlc-docs/inception/business-inputs/` 하위) | 내용 | AI-DLC 스테이지 |
|------|------|-----------------|
| `00_index.md` | 프로젝트 전체 개요 | Requirements Analysis |
| `01_r00-as-is-시스템-분석-종합.md` | AS-IS 분석 (95기능, 600+API) | Reverse Engineering |
| `02_r01-to-be-아키텍처-설계서.md` | C4 아키텍처, 25개 ODA 컴포넌트 | Application Design |
| `03_r02-도메인별-bpm-설계서.md` | 12개 BPMN 프로세스 | Functional Design |
| `05_r03-기능-정의서-oda-기반.md` | ODA 기반 기능 정의 | Application Design |
| `06_r05-통합-데이터-모델-sid-기반.md` | SID 기반 데이터 모델 | Functional Design |
| `07_r06-uiux-설계서.md` | React UI, 70+ 화면 | User Stories |
| `08_r07-as-is-시스템-전환-계획서.md` | Strangler Fig 전환 전략 | Workflow Planning |
| `09_r08-bpm-플랫폼-설계서.md` | Camunda 8 상세 설계 | Infrastructure Design |
| `10_r09-레거시-인터페이스-정의서.md` | TIO/iSigma/CMS Bus/FTP 명세 | Functional Design (U07) |
| `11_r10-보안-아키텍처-설계서.md` | Zero Trust 보안 설계 | NFR Design |
| `12_r11-skt-tmfc-컴포넌트-카탈로그.md` | SKT 고유 18개 컴포넌트 | Application Design |
| `13_r12-프로세스-갭-분석-레포트.md` | eTOM 갭 분석 (매핑률 72%) | Requirements Analysis |
| `14_r13-마이그레이션-로드맵.md` | 3 Phase 로드맵 (2026-2028) | Workflow Planning |

`docs/` 디렉토리는 보존됨 (raw/, tmf-oracle/, research/, templates/, conventions/ 등 하위 자산 — 기획서 14개만 이동).

---

## 디렉토리 구조

```
tgo-im-aidlc/
├── resource-inventory/          # U02 — TMF639 Resource Inventory (Spring Boot)
├── resource-catalog/            # U03 — TMF634 Resource Catalog (Spring Boot)
├── change-management/           # U04 — TMF641/702 Change Management + Camunda 8 BPM (Spring Boot)
├── legacy-integration/          # U07 — TIO/iSigma/CMS Bus Legacy Integration (Spring Boot)
├── ipam-service/                # U08 — IP Address Management (Spring Boot)
├── zone-management/             # U09 — Zone Management 16종 (Spring Boot)
├── topology-service/            # U10 — Neo4j 그래프 Topology (Spring Boot)
├── geographic-site-service/     # U21 — Geographic Site Management (Spring Boot)
├── party-management-service/    # U22 — Party Management (Spring Boot)
├── data-reconciliation/         # U06 — Data Reconciliation Engine (Spring Boot)
├── data-collection/             # U05 — Data Collection Pipeline (Spring Boot)
├── frontend/                    # U11 — React 18 + Vite + TypeScript
├── infra/                       # U01 — Terraform IaC (EKS prod, local-fullstack)
├── config/                      # 환경/서비스 설정 (Checkstyle 등)
├── specs/tmf/                   # TMF 준수 검증 산출물
├── scripts/                     # 빌드/유틸리티
├── docs/raw/                    # TMF 원본 PDF/Excel/UML
├── docs/tmf-oracle/             # TMF Knowledge Oracle (파싱된 .md 청크)
├── docs/research/               # 기술 스택 리서치 노트
├── docs/templates/              # 산출물 템플릿
├── docs/conventions/            # 코딩 컨벤션 메모
│
├── aidlc-docs/                  # 📄 AI-DLC 산출물 (문서 전용)
│   ├── inception/               # 🔵 INCEPTION
│   │   ├── business-inputs/     # 기획서 산출물 (r00~r13)
│   │   ├── reverse-engineering/ # brownfield 표준 9종
│   │   ├── requirements/, application-design/, plans/, user-stories/
│   ├── construction/            # 🟢 CONSTRUCTION (Unit별 설계/코드/빌드 산출물)
│   ├── operations/              # 🟡 OPERATIONS
│   ├── adr/                     # ⭐ Architecture Decision Record SSOT (Nygard)
│   ├── index/                   # 교차 색인 (by-microservice/feature/domain/tmf-api, code-to-doc, adr-index)
│   ├── aidlc-state.md           # 운영 스냅샷
│   └── audit.md                 # 전체 대화/결정 감사 로그 (append-only)
│
├── hub/         # AI 규칙 통합 원장 (AI-DLC + unicli-hub, 모든 AI 도구 공유)
│   ├── common/ inception/ construction/ operations/ extensions/
│   ├── agents/ hooks/ skills/ templates/ memory/
│   └── sync.sh                  # 파생 파일 재생성 (--fix / --check)
└── CLAUDE.md                    # Claude Code 진입점 (sync.sh로 자동 생성)
```

## 코드 위치 규칙

- 애플리케이션 코드: 워크스페이스 루트 (`resource-inventory/`, `resource-catalog/`, `frontend/`, `infra/`)
- Derived directories: `.antigravitycli/`, `.claude/`, `.cursor/`, `.kiro/`, `.codex/`
- 문서/산출물: `aidlc-docs/` 에만 (절대 코드 넣지 않음)
- 기획서 (RFP 입력): `aidlc-docs/inception/business-inputs/`
- 아키텍처 결정 SSOT: `aidlc-docs/adr/` ([`hub/common/adr-conventions.md`](./common/adr-conventions.md))
- TMF 규격 청크: `docs/tmf-oracle/`
- TMF 원본 바이너리: `docs/raw/`

---

## 로컬 Docker 풀스택 환경

원터치 실행: `./infra/local-fullstack/start.sh -d`  (백그라운드) 또는 `./infra/local-fullstack/start.sh`

- **컨테이너 런타임**: Colima (start.sh가 자동 기동, 8 CPU / 12 GB RAM / 80 GB disk)
- **구성**: 인프라 6개 + 앱 서비스 9개 + Nginx 프론트엔드 = 총 16 컨테이너

| 서비스 | 호스트 포트 | 비고 |
|--------|------------|------|
| resource-inventory | 8080 | TMF639 |
| legacy-integration | 8081 | TIO/iSigma/CMS Bus |
| resource-catalog | 8082 | TMF634 |
| change-management | 8083 | Camunda BPM |
| ipam-service | 8084 | IP 관리 |
| topology-service | 8085 | Neo4j |
| data-reconciliation | 8086 | DR 7단계 |
| data-collection | 8087 | FTP/벤더 파서 |
| zone-management | 8092 | 16종 Zone |
| geographic-site-service | 8093 | Geographic Site |
| party-management-service | 8094 | Party Management |
| frontend (nginx) | 3000 | SPA + API 프록시 |
| PostgreSQL | 5432 | |
| Redis | 6379 | |
| Kafka (Redpanda) | 9092 | |
| Neo4j HTTP | 7474 | |
| Zeebe | 26500 | |
| MySQL (IMOWN) | 3307 | |

- **IMOWN 실 데이터**: 123,614건 (AWS staging RDS 덤프, `scripts/tango-im/sample-extract/20260429T1729/`)
  - 10개 테이블 포함: im_eqp_bas (50,000), im_duh_eqp_adtn (45,216), im_acsnw_eqp_addr_inf (12,679) 외 7개
  - `infra/local-fullstack/mysql-init/` — 01 DB/유저 생성 → 02 DDL → 03 gz 덤프 로드
- **주요 설정 이슈 및 해결**:
  - OOM kill 방지: `.env`에서 `JAVA_TOOL_OPTIONS` 전역 설정 제거 (per-service MaxMetaspaceSize 유지)
  - data-collection AWS autoconfigure: `AWS_REGION=ap-northeast-2` + `SPRING_AUTOCONFIGURE_EXCLUDE` 환경변수 필수
  - `--no-build` 플래그: 이미지 캐시 재사용 시 `./start.sh --no-build`

### 단일 서비스 단독 부팅 (풀스택 없이 빠른 검증)

```bash
# 프론트엔드 dev 서버 단독 실행 (백엔드는 local-fullstack 또는 env-var로 datasource 지정)
cd frontend && npm install && npm run dev   # http://localhost:3000
```
