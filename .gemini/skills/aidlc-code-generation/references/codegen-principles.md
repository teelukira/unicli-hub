# Code Generation Principles (MANDATORY for codegen-* subagents)

> **Single source of truth.** Inlining these rules in agent prompts is forbidden — agents must reference this file.

## Origin

- **Karpathy 4 원칙** (출처: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)) — 코드 생성 시 항상 적용
- **Kent Beck TDD** (Red → Green → Refactor) — 각 codegen 서브에이전트의 단계별 절차에 codified (이미 존재)
- 두 원칙은 **직교**: Karpathy = *WHAT to write (quality constraints)*, Beck = *HOW to write it incrementally (process)*

---

## P1 — Think Before Coding

코드를 작성하기 전에 먼저 생각하라.

- 가정을 명시적으로 진술하라. 불확실하면 코드 작성 전에 질문하라 (plan 파일 또는 fix-request로 surface)
- 침묵 선택(silently choose) 대신 복수 해석을 제시하라
- 더 단순한 접근이 보일 때 push back하라
- 혼란 시 멈추고 명확화를 요청하라

> *"State assumptions explicitly; ask rather than guess when uncertain. Present multiple interpretations instead of silently choosing one."* — Karpathy

**Operationalization — Red phase 시작 전:**
- [ ] Plan 파일에서 "확정 변경 영역"을 재확인한다
- [ ] 모호한 요구가 있으면 codegen 에이전트는 *질문 블록*을 fix-request에 기재하고 stop한다

---

## P2 — Simplicity First

문제를 해결하는 최소 코드만 작성하라.

- 추측성 기능, 단일 사용처 추상화, 요청되지 않은 유연성 금지
- 불가능한 시나리오의 에러 핸들링 생략 (경계에서만 검증)
- 시니어 엔지니어 테스트: "이 코드를 over-complicated라 부를까?"

> *"Build minimum code solving the problem only. Avoid speculative features, single-use abstractions, or unrequested flexibility."* — Karpathy

**Operationalization — Refactor phase에서:**
- [ ] DRY 적용은 실제 중복 ≥ 3회일 때만
- [ ] Hexagonal port를 추가하기 전 "이 port가 단일 사용처인가?" 자문
- [ ] 세 줄이 비슷한 코드는 추상화보다 낫다

---

## P3 — Surgical Changes

요청에 직결되는 코드만 변경하라.

- 기존 스타일 매칭 (포매터/네이밍/구조), 본인 선호 강제 금지
- 본인 변경이 만든 import/function만 제거. **사전 dead code는 그대로**
- 변경된 모든 라인은 사용자 요청에 추적 가능해야 한다

> *"Touch only code necessary for the request. Match existing style rather than imposing preferences. Remove only imports/functions YOUR changes orphaned, not pre-existing dead code."* — Karpathy

**Operationalization — Green/Refactor phase:**
- [ ] 변경된 파일이 plan의 "확정 변경 영역" 외부면 STOP
- [ ] git diff 라인 수 inflation 금지 (불필요한 reformat 차단)
- [ ] 모든 변경 라인이 unit 요구사항에 직접 연결됨을 확인

---

## P4 — Goal-Driven Execution

작업을 검증 가능한 성공 기준으로 변환하라.

- Test-first 루프: 테스트 작성 → 통과시키기 → 반복
- 다단계 작업은 검증 체크포인트가 있는 짧은 plan 작성
- 선언적 목표를 사용하라 — 메인 모델이 성공 기준을 정의하면 서브에이전트가 달성한다

> *"LLMs are exceptionally good at looping until they meet specific goals. Don't tell it what to do, give it success criteria and watch it go."* — Karpathy

**Operationalization — Red phase = 성공 기준 정의:**
- [ ] JUnit/Vitest 테스트가 *어떤 동작*을 verify하는지 한 줄로 명시한다
- [ ] 테스트 실패 메시지가 그 자체로 spec이 되어야 한다
- [ ] 각 단계는 짧고 검증 가능한 목표 1개만 가진다

---

## Kent Beck TDD와의 관계

| 사이클 단계 | Karpathy 원칙 적용 |
|------------|-------------------|
| **Red** (실패 테스트 작성) | P1 (가정 명시 후 테스트 설계) + P4 (성공 기준 = 테스트 명세) |
| **Green** (최소 코드로 통과) | P2 (최소 코드) + P3 (변경 영역 최소화) |
| **Refactor** (구조 개선) | P2 (단순화) + P3 (기존 스타일 유지) |

---

## Compliance Gate (codegen 서브에이전트 self-check)

코드 생성 종료 시 각 codegen 서브에이전트는 **반드시** `aidlc-docs/audit.md`에 다음을 append한다:

```markdown
## Codegen Principles Compliance — <agent-name>
**Timestamp**: [ISO 8601]
**Unit**: [unit-name]
- P1 Think Before Coding: [PASS / N/A — reason]
- P2 Simplicity First: [PASS / N/A — reason]
- P3 Surgical Changes: [PASS / N/A — reason]
- P4 Goal-Driven Execution: [PASS / N/A — reason]
- TDD Red→Green→Refactor cycles: [count]
---
```

---

## 위반 시 처리

메인 모델이 subagent dispatch 결과를 검토할 때 P1~P4 또는 TDD 위반을 발견하면:

1. fix-request를 작성하여 **같은 codegen 서브에이전트에 재호출** (`Use the Agent tool with subagent_type`)
2. **절대 메인 모델이 직접 코드를 수정하지 않는다** — Step 10.5의 "메인 모델 직접 코드 작성 금지"와 동일한 원칙
