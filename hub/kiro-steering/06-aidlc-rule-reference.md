---
inclusion: manual
---

# AI-DLC 룰 파일 참조

AI-DLC 워크플로우의 상세 룰은 `hub/` 디렉토리에 있습니다.
각 Construction 단계 작업 시 해당 룰 파일을 반드시 읽고 따르세요.

## 룰 파일 경로 매핑

### 공통 룰 (항상 참조)
- `hub/common/process-overview.md` — 워크플로우 전체 개요
- `hub/common/session-continuity.md` — 세션 재개 가이드
- `hub/common/content-validation.md` — 콘텐츠 검증 규칙
- `hub/common/question-format-guide.md` — 질문 형식 가이드
- `hub/common/depth-levels.md` — 적응형 깊이 레벨
- `hub/common/error-handling.md` — 에러 처리

### Construction 단계 룰 (해당 단계 작업 시 참조)
- `hub/construction/functional-design.md` — Functional Design
- `hub/construction/nfr-requirements.md` — NFR Requirements
- `hub/construction/nfr-design.md` — NFR Design
- `hub/construction/infrastructure-design.md` — Infrastructure Design
- `hub/construction/code-generation.md` — Code Generation
- `hub/construction/build-and-test.md` — Build and Test

### 확장 룰
- `hub/extensions/security/baseline/security-baseline.md`
- `hub/extensions/testing/property-based/property-based-testing.md`

## 사용 방법
Kiro 채팅에서 `#06-aidlc-rule-reference` 로 이 파일을 참조한 뒤,
특정 단계 작업 시 해당 룰 파일을 `#File`로 추가 참조하세요.

예시: U02 NFR Requirements 작업 시
→ `#hub/construction/nfr-requirements.md` 참조
