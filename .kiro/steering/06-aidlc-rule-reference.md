---
inclusion: manual
---

# AI-DLC 룰 파일 참조

AI-DLC 워크플로우의 상세 룰은 `.unicli-rules/` 디렉토리에 있습니다.
각 Construction 단계 작업 시 해당 룰 파일을 반드시 읽고 따르세요.

## 룰 파일 경로 매핑

### 공통 룰 (항상 참조)
- `.unicli-rules/common/process-overview.md` — 워크플로우 전체 개요
- `.unicli-rules/common/session-continuity.md` — 세션 재개 가이드
- `.unicli-rules/common/content-validation.md` — 콘텐츠 검증 규칙
- `.unicli-rules/common/question-format-guide.md` — 질문 형식 가이드
- `.unicli-rules/common/depth-levels.md` — 적응형 깊이 레벨
- `.unicli-rules/common/error-handling.md` — 에러 처리

### Construction 단계 룰 (해당 단계 작업 시 참조)
- `.unicli-rules/construction/functional-design.md` — Functional Design
- `.unicli-rules/construction/nfr-requirements.md` — NFR Requirements
- `.unicli-rules/construction/nfr-design.md` — NFR Design
- `.unicli-rules/construction/infrastructure-design.md` — Infrastructure Design
- `.unicli-rules/construction/code-generation.md` — Code Generation
- `.unicli-rules/construction/build-and-test.md` — Build and Test

### 확장 룰
- `.unicli-rules/extensions/security/baseline/security-baseline.md`
- `.unicli-rules/extensions/testing/property-based/property-based-testing.md`

## 사용 방법
Kiro 채팅에서 `#06-aidlc-rule-reference` 로 이 파일을 참조한 뒤,
특정 단계 작업 시 해당 룰 파일을 `#File`로 추가 참조하세요.

예시: U02 NFR Requirements 작업 시
→ `.unicli-rules/construction/nfr-requirements.md` 참조
