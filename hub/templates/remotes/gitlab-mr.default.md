## 지라 (Jira)

<!-- 예: NWAE-123 NWAE-124 -->

## AI-DLC

- **유닛**: <!-- 예: u25 -->
- **작업 요약**: <!-- AI-DLC 유닛 제목 -->

## 산출물 링크

| 문서 | 경로 |
|------|------|
| 요구사항 | <!-- 예: aidlc-docs/inception/requirements/u25-requirements.md --> |
| 실행 계획 | <!-- 예: aidlc-docs/inception/plans/u25-execution-plan.md --> |
| 코드 생성 계획 | <!-- 예: aidlc-docs/construction/plans/u25-code-generation-plan.md --> |

## 변경 요약

<!-- 무엇을 왜 바꿨는지 항목 1~3개 -->
-
-

## 관련 ADR

<!--
아래에 해당하면 필수 기입:
- 신규 마이크로서비스 / 도메인 분리·통합
- TMF/SID 비준수(NC) 도입 또는 면제
- 주요 기준선 변경 (Spring Boot / Java / React 메이저 등)
- 인프라 토폴로지 변경 (Terraform 모듈 추가·삭제)
- 데이터 권한 이전 (Strangler Fig 단계)
- 인증·보안 모델 변경

형식:
- ADR-NNNN <slug> (예: ADR-0042 new-vector-db-adoption)
- 해당 없음 — "ADR 없음 — 해당 없음" 한 줄 근거 (예: "문서만 수정")
-->

ADR-...

## 영향 범위 (유닛·컴포넌트)

<!-- 영향 받는 AI-DLC 유닛 또는 서비스 -->
-

## 검증

- [ ] 로컬에서 `bash scripts/verify-adr-integrity.sh` 통과
- [ ] 신규 ADR 시 해당 유닛 `INDEX.md`의 `**Relates-To-ADR**` 반영
- [ ] 신규·폐기 ADR 시 `aidlc-docs/index/adr-index.md` 반영
- [ ] QA 테스트 통과 (유닛별)
- [ ] TMF 컴플라이언스 검토 통과 (해당 시)

## 리뷰어 참고 사항

<!-- 특별히 봐야 할 점 -->

---
🤖 ADR 거버넌스: [`hub/extensions/adr/governance/adr-governance.md`](../hub/extensions/adr/governance/adr-governance.md) 준수.
