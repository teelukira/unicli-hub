---
inclusion: manual
---

# AI-DLC Construction Phase 상세 가이드

이 문서는 Construction Phase 작업 시 참조하는 상세 가이드입니다.

## Construction 단계별 실행 순서

### 1. Functional Design (조건부)
- 새로운 데이터 모델, 복잡한 비즈니스 로직이 있을 때 실행
- 산출물: `aidlc-docs/construction/{unit-name}/functional-design/`
- 룰 파일: `.unicli-rules/construction/functional-design.md`

### 2. NFR Requirements (조건부)
- 성능, 보안, 확장성 요구사항이 있을 때 실행
- 질문 파일 생성 → 사용자 답변 수집 → NFR 문서 생성
- 산출물: `aidlc-docs/construction/{unit-name}/nfr-requirements/`
- 룰 파일: `.unicli-rules/construction/nfr-requirements.md`

### 3. NFR Design (조건부)
- NFR Requirements 실행 후 패턴 설계 필요 시
- 산출물: `aidlc-docs/construction/{unit-name}/nfr-design/`
- 룰 파일: `.unicli-rules/construction/nfr-design.md`

### 4. Infrastructure Design (조건부)
- 인프라 서비스 매핑, 배포 아키텍처 필요 시
- 산출물: `aidlc-docs/construction/{unit-name}/infrastructure-design/`
- 룰 파일: `.unicli-rules/construction/infrastructure-design.md`

### 5. Code Generation (필수)
- Part 1: 코드 생성 계획 작성 → 사용자 승인
- Part 2: 계획에 따라 **전문 서브에이전트를 호출**하여 코드 생성 → 체크박스 업데이트
- 계획 파일: `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- 코드: 워크스페이스 루트의 `{unit-name}/src/`
- 룰 파일: `.unicli-rules/construction/code-generation.md`

#### Code Generation 서브에이전트 (4종)

| 서브에이전트 | 전문 영역 | 단축키 | 설정 파일 |
|-------------|----------|--------|----------|
| `codegen-iac` | Terraform/HCL + AWS 공식문서 MCP | `Ctrl+Shift+1` | `.kiro/agents/codegen-iac.json` |
| `codegen-backend` | Java 21 + Spring Boot 3.4.x (Hexagonal) | `Ctrl+Shift+2` | `.kiro/agents/codegen-backend.json` |
| `codegen-frontend` | React 18 + TypeScript | `Ctrl+Shift+3` | `.kiro/agents/codegen-frontend.json` |
| `codegen-db` | Flyway + PostgreSQL + JPA Entity | `Ctrl+Shift+4` | `.kiro/agents/codegen-db.json` |

#### Unit별 서브에이전트 호출 규칙

| Unit 유형 | 호출 서브에이전트 | 호출 순서 |
|----------|-----------------|----------|
| Infrastructure (U01) | `codegen-iac` | 단독 |
| Database (U01-DB) | `codegen-db` | 단독 |
| Backend Service (U02~U10) | `codegen-db` → `codegen-backend` | DB 먼저 (스키마 의존) |
| Frontend (U11) | `codegen-frontend` | 단독 |

#### 호출 방법
```
# Part 2 각 Step 실행 시 해당 서브에이전트 호출
use_subagent → InvokeSubagents
  agent_name: "{서브에이전트명}"
  query: "{Unit} Step {N}: {step 설명}"
  relevant_context: "aidlc-docs/construction/plans/{unit}-code-generation-plan.md 의 Step {N}"
```

#### 주의사항
- DB 스키마에 의존하는 JPA 엔티티는 `codegen-db` 완료 후 `codegen-backend` 호출
- 독립적인 Step은 병렬 호출 가능 (use_subagent의 subagents 배열 활용)
- 서브에이전트는 코드만 생성, 체크박스 업데이트와 audit 로깅은 메인 에이전트가 수행

### 6. Build and Test (필수)
- 모든 Unit 완료 후 실행
- **독립 QA 에이전트(`qa-tester`)가 빌드/테스트 수행** (코드 생성 에이전트와 분리, 긍정 편향 방지)
- **TMF Unit은 추가로 `tmf-compliance-reviewer`가 표준 준수 검증**
- 산출물: `aidlc-docs/construction/build-and-test/`
- 룰 파일: `.unicli-rules/construction/build-and-test.md`

#### Build and Test 서브에이전트

| 서브에이전트 | 역할 | 단축키 | 설정 파일 |
|-------------|------|--------|----------|
| `qa-tester` | 빌드 실행, 테스트 실행, 결과 분석, 실패 진단 | `Ctrl+Shift+5` | `.kiro/agents/qa-tester.json` |
| `tmf-compliance-reviewer` | TMF-01~TMF-09 표준 준수 검증 | `Ctrl+Shift+6` | `.kiro/agents/tmf-compliance-reviewer.json` |
| `web-integration-tester` | API 스키마 검증 + Playwright E2E 브라우저 테스트 | `Ctrl+Shift+7` | `.kiro/agents/web-integration-tester.json` |

#### 호출 흐름

```
Code Generation 완료
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
[Complete] 전체 PASS → Build and Test 완료
```

#### 피드백 루프 규칙
- qa-tester/tmf-compliance-reviewer/web-integration-tester는 코드를 **절대 수정하지 않음** (읽기 + 실행 + 분석만)
- 실패 시 수정 요청서(fix-request)를 생성하여 해당 codegen 에이전트에 위임
- codegen 에이전트가 수정 완료 후 해당 검증 에이전트가 재검증 (fresh verification)
- 최대 3회 반복 후 실패 시 사용자에게 에스컬레이션
- 3종 에이전트 모두 독립적이므로 병렬 호출 가능

## 필수 규칙
- 코드는 워크스페이스 루트에만 생성 (aidlc-docs/ 아님)
- 계획 체크박스는 작업 완료 즉시 [x]로 업데이트
- 모든 단계에서 사용자 승인 대기 (2-option: Request Changes / Continue)
- audit.md에 모든 상호작용 기록 (ISO 8601 타임스탬프)
- aidlc-state.md 진행 상태 즉시 업데이트

## TMF Open API 참조
- TMF639: Resource Inventory Management
- TMF634: Resource Catalog Management
- TMF641: Service Ordering Management
- TMF642: Alarm Management
- TMF702: Resource Activation Management
- TMF621: Trouble Ticket Management
- 스펙 파일: `api-specs/` 디렉토리
