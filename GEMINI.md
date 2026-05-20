# GEMINI.md

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
| U03 | Resource Catalog (TMF634) | 85% | 카탈로그 초기 데이터 | ✅ 완료 (TMF CONDITIONAL PASS) |
| U04 | Change Management (BPM + Camunda) | 60% | 보상 트랜잭션, 부분 성공 정책 | ✅ 완료 (TMF CONDITIONAL PASS) |
| U05 | Data Collection Pipeline (FTP + 50+ 벤더 파서) | 40% | **벤더별 파서 로직 (반드시 인간 검증)** | ✅ 완료 (QA PASS 27/27, TMF PASS) |
| U06 | Data Reconciliation Engine (DR 7단계) | 55% | DR 정책, 자동화 임계값 | ✅ 완료 (QA PASS 41/41) |
| U07 | Legacy Integration Hub (TIO/iSigma/CMS Bus) | 35% | **바이너리 프로토콜 오프셋 검증 필수** | ✅ 완료 (TMF PASS — U99 재검증 PASS) |
| U08 | IP Address Management | 75% | CIDR 할당 정책 | ✅ 완료 (TMF PASS) |
| U09 | Zone Management (16종 Zone) | 70% | Zone 비즈니스 룰 | ✅ 완료 (TMF PASS — U09-Redo+U99 재검증 PASS) |
| U10 | Topology Service (Neo4j) | 50% | 그래프 관계 정의 | ✅ 완료 (TMF PASS — U99 재검증 PASS) |
| U11 | Frontend MVP (React 18 + ATOM DS) | 75% | SKT ATOM Design System UX | ✅ 완료 |
| U12 | Auth Governance (Keycloak + RBAC) | 80% | 역할별 권한 매트릭스 | ⏸ 대기 |
| U13 | Tango-I-DB Legacy Migration | 65% | **IMOWN 9 테이블 매핑 인간 검증 필수**, OID 정합성 확인 | ✅ 완료 (QA PASS, TMF PASS) |
| U14 | Legacy Topology Projection | 70% | RI Canonical Kafka Outbox, 그래프 관계 정의 | ✅ 완료 (QA PASS, TMF PASS) |
| U15 | TM Forum CTK Runtime Conformance | 75% | Docker/Newman orchestration 검증 | ✅ 완료 |
| U16 | TMF CTK ↔ Local Docker Stack Integration | 80% | CTK matrix 실행 환경, DNS 통합 | ✅ 완료 |
| U24 | TMF NC Remediation (W-3/W-4/W1/W2 4건 해소) | 90% | — | ✅ BT 완료 (GATE-TMF PASS run-07, 활성 NC waive 0건) |

> **실시간 상태는 [`aidlc-docs/aidlc-state.md`](aidlc-docs/aidlc-state.md)가 단일 진실 공급원 (single source of truth).** 본 테이블의 상태 컬럼은 스냅샷이며 동기화 지연이 있을 수 있음.

---

## Current Progress (2026-05-13 스냅샷)

- **Inception Phase**: 전체 완료 (User Stories는 skip — API 백엔드 중심, 기획서 기능 정의로 충분)
- **Construction Phase (완료)**: U01 / U01-DB / U02 / U03 / U04 / U05 / U06 / U07 / U08 / U09 / U10 / U11 / U11-Iteration / U13 / U14 / U15 / U16 전체 코드 생성 및 `main` 병합 완료
- **U24 TMF NC Remediation**: ✅ BT 완료, MR 준비 중 — W-3(GeographicSubAddress), W-4(ProfileGuard), W1(OrganizationStatus), W2(Hub/Outbox). **활성 TMF NC waive 0건 (specs/tmf/_summary.md run-07)**.
- **U99 TMF Re-verification**: ✅ 모든 unit PASS (U03/U04/U07/U09/U10 재검증 완료)
- **로컬 Docker 풀스택**: ✅ 완료 (`infra/local-fullstack/` — Colima + 16 컨테이너 원터치, IMOWN 실 데이터 123,614건)
- **Dev-Light 경량 배포**: ✅ 배포 완료 (ECS Fargate + S3/CloudFront)
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
├── legacy-integration-hub/      # U07 — TIO/iSigma/CMS Bus Legacy Integration (Spring Boot)
├── ipam-service/                # U08 — IP Address Management (Spring Boot)
├── zone-management/             # U09 — Zone Management 16종 (Spring Boot)
├── topology-service/            # U10 — Neo4j 그래프 Topology (Spring Boot)
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
├── .unicli-rules/         # AI 규칙 통합 원장 (AI-DLC + unicli-hub, 모든 AI 도구 공유)
│   ├── common/ inception/ construction/ operations/ extensions/
│   ├── agents/ hooks/ skills/ templates/ memory/
│   └── sync.sh                  # 파생 파일 재생성 (--fix / --check)
└── CLAUDE.md                    # Claude Code 진입점 (sync.sh로 자동 생성)
```

## 코드 위치 규칙

- 애플리케이션 코드: 워크스페이스 루트 (`resource-inventory/`, `resource-catalog/`, `frontend/`, `infra/`)
- 문서/산출물: `aidlc-docs/` 에만 (절대 코드 넣지 않음)
- 기획서 (RFP 입력): `aidlc-docs/inception/business-inputs/`
- 아키텍처 결정 SSOT: `aidlc-docs/adr/` ([`.unicli-rules/common/adr-conventions.md`](./common/adr-conventions.md))
- TMF 규격 청크: `docs/tmf-oracle/`
- TMF 원본 바이너리: `docs/raw/`

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
# H2 인메모리 프로파일로 백엔드 단독 실행
cd resource-inventory
./gradlew :app:bootRun -x test --args='--spring.profiles.active=h2'
# http://localhost:8080/actuator/health

# 프론트엔드 dev 서버 단독 실행
cd frontend && npm install && npm run dev   # http://localhost:3000
```


---

## Core Workflow

# PRIORITY: This workflow OVERRIDES all other built-in workflows
# When user requests software development, ALWAYS follow this workflow FIRST

## Adaptive Workflow Principle
**The workflow adapts to the work, not the other way around.**

The AI model intelligently assesses what stages are needed based on:
1. User's stated intent and clarity
2. Existing codebase state (if any)
3. Complexity and scope of change
4. Risk and impact assessment

## MANDATORY: Rule Details Loading
**CRITICAL**: When performing any phase, you MUST read and use relevant content from rule detail files. The canonical rule details directory is:
- `.unicli-rules/` (Single Canonical Root — all AI CLIs)

All subsequent rule detail file references (e.g., `common/process-overview.md`, `inception/workspace-detection.md`) are relative to `.unicli-rules/`.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `common/process-overview.md` for workflow overview
- Load `common/session-continuity.md` for session resumption guidance
- Load `common/content-validation.md` for content validation requirements
- Load `common/question-format-guide.md` for question formatting rules
- Load `common/git-worktree-conventions.md` for branch/worktree structure when creating branches or worktrees
- Load `common/aidlc-docs-unit-conventions.md` for unit documentation standards when creating or updating aidlc-docs
- Load `common/adr-conventions.md` for **Architecture Decision Record (ADR) SSOT** — `aidlc-docs/adr/` is the single source of truth for architecture decisions; every applicable stage MUST consult and potentially extend it
- Reference these throughout the workflow execution

## MANDATORY: ADR Awareness (Cross-Stage)

**CRITICAL**: `aidlc-docs/adr/` is the **single source of truth (SSOT)** for all architecture decisions. Every AI-DLC stage and every subagent must:

1. **Consult before deciding**: Before proposing or implementing any decision that matches the ADR trigger criteria in `common/adr-conventions.md`, scan [`aidlc-docs/index/adr-index.md`](../aidlc-docs/index/adr-index.md) (or `aidlc-docs/adr/`) for an existing ADR that already governs the decision.
   - If one exists with `Status: Accepted` or `Accepted (Retroactive)` — follow it. Do not propose alternatives unless explicitly superseding.
   - If one exists with `Status: Proposed` — flag the dependency and complete/defer accordingly.
   - If none exists and the decision is architecturally significant — invoke the `adr-curator` subagent to draft a new ADR before continuing.
2. **Cite in artifacts**: Stage outputs (functional-design, code-generation plans, etc.) MUST cite related ADR numbers when the artifact reflects a decision (e.g., `Relates-To-ADR: 0005, 0006`).
3. **Verify backlinks**: Whenever updating a `aidlc-docs/construction/{unit}/INDEX.md`, ensure the top `**Relates-To-ADR**:` line is present and up-to-date.
4. **Respect supersede chain**: Never resurrect decisions whose ADR is `Status: Superseded by NNNN` or `Deprecated` without creating a new ADR.

**Enforcement**: When the `ADR Governance` extension is `Enabled (Full)` in `aidlc-docs/aidlc-state.md`, missing ADRs or stale backlinks become blocking findings — see `extensions/adr/governance/adr-governance.md`.

**Tooling support**:
- Subagent `adr-curator` drafts/reviews ADRs in Nygard format.
- Subagent `adr-impact-scanner` analyzes diffs for ADR impact.
- Script `scripts/verify-adr-integrity.sh` validates metadata + backlinks + supersede chain.
- PostToolUse hook `adr_backlink_check.py` guards unit INDEX edits.

## MANDATORY: Extensions Loading (Context-Optimized)
**CRITICAL**: At workflow start, scan the `extensions/` directory recursively but load ONLY lightweight opt-in files — NOT full rule files. Full rule files are loaded on-demand after the user opts in.

**Loading process**:
1. List all subdirectories under `extensions/` (e.g., `extensions/security/`, `extensions/compliance/`)
2. In each subdirectory, load ONLY `*.opt-in.md` files — these contain the extension's opt-in prompt. The corresponding rules file is derived by convention: strip the `.opt-in.md` suffix and append `.md` (e.g., `security-baseline.opt-in.md` → `security-baseline.md`)
3. Do NOT load full rule files (e.g., `security-baseline.md`) at this stage

**Deferred Rule Loading**:
- During Requirements Analysis, opt-in prompts from the loaded `*.opt-in.md` files are presented to the user
- When the user opts IN for an extension, load the corresponding rules file (derived by naming convention) at that point
- When the user opts OUT, the full rules file is never loaded — saving context
- Extensions without a matching `*.opt-in.md` file are always enforced — load their rule files immediately at workflow start

**Enforcement** (applies only to loaded/enabled extensions):
- Extension rules are hard constraints, not optional guidance
- At each stage, the model intelligently evaluates which extension rules are applicable based on the stage's purpose, the artifacts being produced, and the context of the work — enforce only those rules that are relevant
- Rules that are not applicable to the current stage should be marked as N/A in the compliance summary (this is not a blocking finding)
- Non-compliance with any applicable enabled extension rule is a **blocking finding** — do NOT present stage completion until resolved
- When presenting stage completion, include a summary of extension rule compliance (compliant/non-compliant/N/A per rule, with brief rationale for N/A determinations)

**Conditional Enforcement**: Extensions may be conditionally enabled/disabled. See `inception/requirements-analysis.md` for the opt-in mechanism. Before enforcing any extension at ANY stage, check its `Enabled` status in `aidlc-docs/aidlc-state.md` under `## Extension Configuration`. Skip disabled extensions and log the skip in audit.md. Default to enforced if no configuration exists.

## MANDATORY: Content Validation
**CRITICAL**: Before creating ANY file, you MUST validate content according to `common/content-validation.md` rules:
- Validate Mermaid diagram syntax
- Validate ASCII art diagrams (see `common/ascii-diagram-standards.md`)
- Escape special characters properly
- Provide text alternatives for complex visual content
- Test content parsing compatibility

## MANDATORY: Question File Format
**CRITICAL**: When asking questions at any phase, you MUST follow question format guidelines.

**See `common/question-format-guide.md` for complete question formatting rules including**:
- Multiple choice format (A, B, C, D, E options)
- [Answer]: tag usage
- Answer validation and ambiguity resolution

## MANDATORY: Custom Welcome Message
**CRITICAL**: When starting ANY software development request, you MUST display the welcome message.

**How to Display Welcome Message**:
1. Load the welcome message from `common/welcome-message.md` (in the resolved rule details directory)
2. Display the complete message to the user
3. This should only be done ONCE at the start of a new workflow
4. Do NOT load this file in subsequent interactions to save context space

# Adaptive Software Development Workflow

---

# INCEPTION PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in INCEPTION PHASE**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (CONDITIONAL)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)
- Units Generation (CONDITIONAL)

---

## Workspace Detection (ALWAYS EXECUTE)

1. **MANDATORY**: Log initial user request in audit.md with complete raw input
2. Load all steps from `inception/workspace-detection.md`
3. Execute workspace detection:
   - Check for existing aidlc-state.md (resume if found)
   - Scan workspace for existing code
   - Determine if brownfield or greenfield
   - Check for existing reverse engineering artifacts
4. Determine next phase: Reverse Engineering (if brownfield and no artifacts) OR Requirements Analysis
5. **MANDATORY**: Log findings in audit.md
6. Present completion message to user (see workspace-detection.md for message formats)
7. Automatically proceed to next phase

## Reverse Engineering (CONDITIONAL - Brownfield Only)

**Execute IF**:
- Existing codebase detected
- No previous reverse engineering artifacts found

**Skip IF**:
- Greenfield project
- Previous reverse engineering artifacts exist

**Execution**:
1. **MANDATORY**: Log start of reverse engineering in audit.md
2. Load all steps from `inception/reverse-engineering.md`
3. Execute reverse engineering:
   - Analyze all packages and components
   - Generate a business overview of the whole system covering the business transactions
   - Generate architecture documentation
   - Generate code structure documentation
   - Generate API documentation
   - Generate component inventory
   - Generate Interaction Diagrams depicting how business transactions are implemented across components
   - Generate technology stack documentation
   - Generate dependencies documentation

4. **Wait for Explicit Approval**: Present detailed completion message (see reverse-engineering.md for message format) - DO NOT PROCEED until user confirms
5. **MANDATORY**: Log user's response in audit.md with complete raw input

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes** but depth varies based on request clarity and complexity:
- **Minimal**: Simple, clear request - just document intent analysis
- **Standard**: Normal complexity - gather functional and non-functional requirements
- **Comprehensive**: Complex, high-risk - detailed requirements with traceability

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/requirements-analysis.md`
3. Execute requirements analysis:
   - Load reverse engineering artifacts (if brownfield)
   - Analyze user request (intent analysis)
   - Determine requirements depth needed
   - Assess current requirements
   - Ask clarifying questions (if needed)
   - Generate requirements document
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Follow approval format from requirements-analysis.md detailed steps - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

## User Stories (CONDITIONAL)

**INTELLIGENT ASSESSMENT**: Use multi-factor analysis to determine if user stories add value:

**ALWAYS Execute IF** (High Priority Indicators):
- New user-facing features or functionality
- Changes affecting user workflows or interactions
- Multiple user types or personas involved
- Complex business requirements with acceptance criteria needs
- Cross-functional team collaboration required
- Customer-facing API or service changes
- New product capabilities or enhancements

**LIKELY Execute IF** (Medium Priority - Assess Complexity):
- Modifications to existing user-facing features
- Backend changes that indirectly affect user experience
- Integration work that impacts user workflows
- Performance improvements with user-visible benefits
- Security enhancements affecting user interactions
- Data model changes affecting user data or reports

**COMPLEXITY-BASED ASSESSMENT**: For medium priority cases, execute user stories if:
- Request involves multiple components or services
- Changes span multiple user touchpoints
- Business logic is complex or has multiple scenarios
- Requirements have ambiguity that stories could clarify
- Implementation affects multiple user journeys
- Change has significant business impact or risk

**SKIP ONLY IF** (Low Priority - Simple Cases):
- Pure internal refactoring with zero user impact
- Simple bug fixes with clear, isolated scope
- Infrastructure changes with no user-facing effects
- Technical debt cleanup with no functional changes
- Developer tooling or build process improvements
- Documentation-only updates

**ASSESSMENT CRITERIA**: When in doubt, favor inclusion of user stories for:
- Requests with business stakeholder involvement
- Changes requiring user acceptance testing
- Features with multiple implementation approaches
- Work that benefits from shared team understanding
- Projects where requirements clarity is valuable

**ASSESSMENT PROCESS**:
1. Analyze request complexity and scope
2. Identify user impact (direct or indirect)
3. Evaluate business context and stakeholder needs
4. Consider team collaboration benefits
5. Default to inclusion for borderline cases

**Note**: If Requirements Analysis executed, Stories can reference and build upon those requirements.

**User Stories has two parts within one stage**:
1. **Part 1 - Planning**: Create story plan with questions, collect answers, analyze for ambiguities, get approval
2. **Part 2 - Generation**: Execute approved plan to generate stories and personas

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/user-stories.md`
3. **MANDATORY**: Perform intelligent assessment (Step 1 in user-stories.md) to validate user stories are needed
4. Load reverse engineering artifacts (if brownfield)
5. If Requirements exist, reference them when creating stories
6. Execute at appropriate depth (minimal/standard/comprehensive)
7. **PART 1 - Planning**: Create story plan with questions, wait for user answers, analyze for ambiguities, get approval
8. **PART 2 - Generation**: Execute approved plan to generate stories and personas
9. **Wait for Explicit Approval**: Follow approval format from user-stories.md detailed steps - DO NOT PROCEED until user confirms
10. **MANDATORY**: Log user's response in audit.md with complete raw input

## Workflow Planning (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/workflow-planning.md`
3. **MANDATORY**: Load content validation rules from `common/content-validation.md`
4. Load all prior context:
   - Reverse engineering artifacts (if brownfield)
   - Intent analysis
   - Requirements (if executed)
   - User stories (if executed)
5. Execute workflow planning:
   - Determine which phases to execute
   - Determine depth level for each phase
   - Create multi-package change sequence (if brownfield)
   - Generate workflow visualization (VALIDATE Mermaid syntax before writing)
6. **MANDATORY**: Validate all content before file creation per content-validation.md rules
7. **Wait for Explicit Approval**: Present recommendations using language from workflow-planning.md Step 9, emphasizing user control to override recommendations - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input

## Application Design (CONDITIONAL)

**Execute IF**:
- New components or services needed
- Component methods and business rules need definition
- Service layer design required
- Component dependencies need clarification

**Skip IF**:
- Changes within existing component boundaries
- No new components or methods
- Pure implementation changes

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/application-design.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see application-design.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

## Units Generation (CONDITIONAL)

**Execute IF**:
- System needs decomposition into multiple units of work
- Multiple services or modules required
- Complex system requiring structured breakdown

**Skip IF**:
- Single simple unit
- No decomposition needed
- Straightforward single-component implementation

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/units-generation.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see units-generation.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

---

# 🟢 CONSTRUCTION PHASE

**Purpose**: Detailed design, NFR implementation, and code generation

**Focus**: Determine HOW to build it

**Stages in CONSTRUCTION PHASE**:
- Per-Unit Loop (executes for each unit):
  - Functional Design (CONDITIONAL, per-unit)
  - NFR Requirements (CONDITIONAL, per-unit)
  - NFR Design (CONDITIONAL, per-unit)
  - Infrastructure Design (CONDITIONAL, per-unit)
  - Code Generation (ALWAYS, per-unit)
  - Build and Test (ALWAYS, per-unit — runs immediately after Code Generation)

**Note**: Each unit is completed fully (design + code + build/test/QA) before moving to the next unit.

---

## Per-Unit Loop (Executes for Each Unit)

**For each unit of work, execute the following stages in sequence:**

### Functional Design (CONDITIONAL, per-unit)

**Execute IF**:
- New data models or schemas
- Complex business logic
- Business rules need detailed design

**Skip IF**:
- Simple logic changes
- No new business logic

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/functional-design.md`
3. Execute functional design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in functional-design.md - DO NOT use emergent 3-option behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Requirements (CONDITIONAL, per-unit)

**Execute IF**:
- Performance requirements exist
- Security considerations needed
- Scalability concerns present
- Tech stack selection required

**Skip IF**:
- No NFR requirements
- Tech stack already determined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-requirements.md`
3. Execute NFR assessment for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-requirements.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Design (CONDITIONAL, per-unit)

**Execute IF**:
- NFR Requirements was executed
- NFR patterns need to be incorporated

**Skip IF**:
- No NFR requirements
- NFR Requirements was skipped

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-design.md`
3. Execute NFR design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### Infrastructure Design (CONDITIONAL, per-unit)

**Execute IF**:
- Infrastructure services need mapping
- Deployment architecture required
- Cloud resources need specification

**Skip IF**:
- No infrastructure changes
- Infrastructure already defined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/infrastructure-design.md`
3. Execute infrastructure design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in infrastructure-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### Code Generation (ALWAYS EXECUTE, per-unit)

**Always executes for each unit**

**Code Generation has two parts within one stage**:
1. **Part 1 - Planning**: Create detailed code generation plan with explicit steps
2. **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/code-generation.md`
3. **PART 1 - Planning**: Create code generation plan with checkboxes, get user approval
4. **PART 2 - Generation**: Execute approved plan to generate code for this unit
5. **MANDATORY**: Present standardized 2-option completion message as defined in code-generation.md - DO NOT use emergent behavior
6. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input

### Build and Test (ALWAYS EXECUTE, per-unit)

**Always executes immediately after Code Generation for each unit**

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/build-and-test.md`
3. Execute build and test for this unit:
   - Step 1.5: Determine unit scope and set verification gate checklist (qa-tester / tmf-reviewer / web-integration-tester)
   - Step 2.5: Invoke `qa-tester` subagent — **BLOCKING**, must PASS before continuing
   - Step 4.5: Invoke `tmf-compliance-reviewer` subagent (if TMF-standard unit) — **BLOCKING** if mandatory
   - Step 5.5: Invoke `web-integration-tester` subagent (if frontend/mixed unit)
4. **MANDATORY**: DO NOT mark Build and Test `[x]` complete until ALL gates pass:
   - `qa-tester` = PASS
   - `tmf-compliance-reviewer` = PASS or N/A
   - `web-integration-tester` = PASS, CONDITIONAL PASS, or N/A
5. **MANDATORY**: Present standardized 2-option completion message as defined in build-and-test.md - DO NOT use emergent behavior
6. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input

---

# 🟡 OPERATIONS PHASE

**Purpose**: Placeholder for future deployment and monitoring workflows

**Focus**: How to DEPLOY and RUN it (future expansion)

**Stages in OPERATIONS PHASE**:
- Operations (PLACEHOLDER)

---

## Operations (PLACEHOLDER)

**Status**: This stage is currently a placeholder for future expansion.

The Operations stage will eventually include:
- Deployment planning and execution
- Monitoring and observability setup
- Incident response procedures
- Maintenance and support workflows
- Production readiness checklists

**Current State**: All per-unit build/test/QA/TMF verification is handled in the CONSTRUCTION phase (per-unit Build and Test stage).

## Key Principles

- **Adaptive Execution**: Only execute stages that add value
- **Transparent Planning**: Always show execution plan before starting
- **User Control**: User can request stage inclusion/exclusion
- **Progress Tracking**: Update aidlc-state.md with executed and skipped stages
- **Complete Audit Trail**: Log ALL user inputs and AI responses in audit.md with timestamps
  - **CRITICAL**: Capture user's COMPLETE RAW INPUT exactly as provided
  - **CRITICAL**: Never summarize or paraphrase user input in audit log
  - **CRITICAL**: Log every interaction, not just approvals
- **Quality Focus**: Complex changes get full treatment, simple changes stay efficient
- **Content Validation**: Always validate content before file creation per content-validation.md rules
- **NO EMERGENT BEHAVIOR**: Construction phases MUST use standardized 2-option completion messages as defined in their respective rule files. DO NOT create 3-option menus or other emergent navigation patterns.

## MANDATORY: Plan-Level Checkbox Enforcement

### MANDATORY RULES FOR PLAN EXECUTION
1. **NEVER complete any work without updating plan checkboxes**
2. **IMMEDIATELY after completing ANY step described in a plan file, mark that step [x]**
3. **This must happen in the SAME interaction where the work is completed**
4. **NO EXCEPTIONS**: Every plan step completion MUST be tracked with checkbox updates

### Two-Level Checkbox Tracking System
- **Plan-Level**: Track detailed execution progress within each stage
- **Stage-Level**: Track overall workflow progress in aidlc-state.md
- **Update immediately**: All progress updates in SAME interaction where work is completed

## Prompts Logging Requirements
- **MANDATORY**: Log EVERY user input (prompts, questions, responses) with timestamp in audit.md
- **MANDATORY**: Capture user's COMPLETE RAW INPUT exactly as provided (never summarize)
- **MANDATORY**: Log every approval prompt with timestamp before asking the user
- **MANDATORY**: Record every user response with timestamp after receiving it
- **CRITICAL**: ALWAYS append changes to EDIT audit.md file, NEVER use tools and commands that completely overwrite its contents
- **CRITICAL**: NEVER use file writing tools and commands that overwrite the entire contents of audit.md, as this causes duplication
- Use ISO 8601 format for timestamps (YYYY-MM-DDTHH:MM:SSZ)
- Include stage context for each entry

### Audit Log Format:
```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Input**: "[Complete raw user input - never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

### Correct Tool Usage for audit.md

✅ CORRECT:

1. Read the audit.md file
2. Append/Edit the file to make changes

❌ WRONG:

1. Read the audit.md file
2. Completely overwrite the audit.md with the contents of what you read, plus the new changes you want to add to it

## Directory Structure

```text
<WORKSPACE-ROOT>/                   # ⚠️ APPLICATION CODE HERE
├── [project-specific structure]    # Varies by project (see code-generation.md)
│
├── aidlc-docs/                     # 📄 DOCUMENTATION ONLY
│   ├── inception/                  # 🔵 INCEPTION PHASE
│   │   ├── plans/
│   │   ├── reverse-engineering/    # Brownfield only
│   │   ├── requirements/
│   │   ├── user-stories/
│   │   └── application-design/
│   ├── construction/               # 🟢 CONSTRUCTION PHASE
│   │   ├── plans/
│   │   ├── {unit-name}/
│   │   │   ├── functional-design/
│   │   │   ├── nfr-requirements/
│   │   │   ├── nfr-design/
│   │   │   ├── infrastructure-design/
│   │   │   └── code/               # Markdown summaries only
│   │   └── build-and-test/
│   ├── operations/                 # 🟡 OPERATIONS PHASE (placeholder)
│   ├── aidlc-state.md
│   └── audit.md
```

## Generated File Rules
**Never edit derived files directly**:

- `CLAUDE.md`, `AGENTS.md` at the repository root
- `.claude/agents/*.md`
- `.cursor/rules/*.mdc`, `.cursor/agents/*.md`
- `GEMINI.md` (repo root), `.gemini/agents/*.md`, `.gemini/skills/*/SKILL.md`
- `.kiro/steering/*.md`, `.kiro/agents/prompts/*`
- `.codex/prompts/*.md`
- MCP: `.mcp.json`, `.cursor/mcp.json`, `.kiro/mcp.json`, `.gemini/settings.json` (`mcpServers`), `.codex/config.toml` (MCP block)

**Edit here instead**: `.unicli-rules/` (the canonical source).
After editing, run `./.unicli-rules/sync.sh --fix` to regenerate every derived file.


---

## Memory

# Project Facts

> **Template.** Fill in the real project facts. Leaving vague "TBD" values actively hurts AI output — be specific or delete the section.

## Team / Owner

- _TBD — responsible team or individual, Slack channel, issue tracker._

## Repository

- Primary repo: _TBD_
- Branching model: _TBD (trunk-based, gitflow, ...)_
- Default branch: `main`

## Core Decisions

- _TBD — irreversible technical choices and the reason behind them (one line each)._
- _Example: "Chose DynamoDB over PostgreSQL because of latency SLA."_

## Environments

- _TBD — dev / staging / prod endpoints and how each is deployed._

## Stakeholders

- _TBD — owners of external interfaces, reviewers._


# Conventions

Project-wide code and documentation conventions live here. AI CLIs generating or editing code must honor them.

## Code Style

- Comments: **default to none**. Add a single line only when the *why* is non-obvious.

## Test Policy

- Frontend E2E: local-server (Playwright `webServer`) is mandatory for
  frontend units' Build and Test gate. Mock-based or backend-skipped E2E
  does not satisfy this requirement.

## Security

- Secrets: `.env` or secret manager — never commit.
- User input is validated at boundaries; trust internal code.


---
name: jira-config
description: Default Jira project/epic/assignee for AI-DLC workflow auto-ticketing (project=NWAE, epic=[nOSS]TANGO-I, default developer=류근호)
type: project
---

# Jira Integration Config

## Defaults

```yaml
project_key: NWAE
epic_name: "[nOSS]TANGO-I"
epic_key: "NWAE-326"              # Epic Link 연결 키 (.env.example AI_DLC_JIRA_EPIC_KEY)
epic_field: "customfield_10001"   # Jira Server Epic Link 필드 ID (jira_create_issue additional_fields로 전달)
issue_type: "작업(Task)"           # Discovery 2026-05-13 확인 (Story 아님)
reporter: 류근호
assignee: 류근호
assignee_username: "1111207"      # MCP jira_create_issue assignee 인자 — 표시 이름(류근호) 아닌 username 사용
transition_id_inprogress: "21"    # "Start Progress"  To Do → 진행중(In Progress)
transition_id_done: "111"         # "Resolve"  In Progress → 검토(Review) [완료 카테고리]
required_custom_fields: {}         # Auto-populated by try-parse-retry Discovery
```

## MCP 도구 사용 시 주의사항

**담당자(Assignee)**
- `jira_create_issue`의 `assignee` 파라미터: **표시 이름("류근호") 아닌 username("1111207")** 전달
- 표시 이름은 이 Jira Server 인스턴스에서 조용히 실패하고 Unassigned로 생성됨 (2026-05-14 확인)

**에픽(Epic Link)**
- `jira_create_issue`의 `additional_fields`로 전달: `{"customfield_10001": "NWAE-326"}`
- Jira Server/DC는 `epicKey` 단축 파라미터 미지원 — 반드시 `customfield_10001` 사용
- 에픽 키: `NWAE-326` (.env.example `AI_DLC_JIRA_EPIC_KEY` 기준)

## Developer Overrides

개발자별 설정 변경은 **`memory/jira-config.local.md`** 파일 생성 (gitignored).
예시는 `memory/jira-config.local.md.example` 참조.

우선순위: `jira-config.local.md` > 이 파일 (기본값).

**Why:** 보고자/작업자를 개발자마다 다르게 설정하되 프로젝트 공통 설정(project_key, epic)은 공유.
**How to apply:** Jira 티켓 생성 전 local override를 먼저 로드하고, 없는 필드는 이 파일에서 채움.

### 템플릿 렌더용 환경변수 (선택)

Jira 이슈 **본문(description)** 렌더 시 담당/보고를 JSON 대신 루트 `.env` / `.env.local`에서 쓰려면 `AI_DLC_JIRA_ASSIGNEE`, `AI_DLC_JIRA_REPORTER`를 설정하세요. (`scripts/render-ai-dlc-remote-templates.py --target jira`, 루트 `.env.example` 참고.) MCP로 이슈를 만들 때의 `assignee` / `reporter` 인자는 위 YAML 기본값·local md가 우선입니다.



# Glossary

Keep project-specific terminology here. Any word that is used with a meaning different from plain English must be recorded.

| Term | Definition | Note |
|------|------------|------|
| _TBD_ | _TBD_ | _TBD_ |

## Abbreviations

| Abbreviation | Full | Context |
|--------------|------|---------|
| _TBD_ | _TBD_ | _TBD_ |



