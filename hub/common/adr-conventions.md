# Architecture Decision Records (ADR) 컨벤션

## 개요

본 프로젝트의 **모든 아키텍처 결정**은 [`aidlc-docs/adr/`](../../aidlc-docs/adr/)에 ADR로 영구 기록한다. ADR이 **단일 SSOT**이며, 결정의 권위(authority)는 ADR에 있다. 결정의 변경도 새 ADR로 영구화한다.

## SSOT 위계

| 산출물 | 역할 | 권위 |
|---|---|---|
| `aidlc-docs/audit.md` | raw 사료 (append-only, 사용자 입력 원문) | 1차 |
| `aidlc-docs/adr/**` | **정제된 결정 (SSOT)** | **결정의 권위** |
| `aidlc-docs/aidlc-state.md` | 현재 운영 스냅샷 | 스냅샷 |
| `aidlc-docs/construction/{unit}/` | unit별 산출물 | unit 컨텍스트 |

**충돌 원칙**: 문서와 실제 구현 코드가 충돌하면 **코드가 진실의 원천(source of truth)**. 결정은 ADR로 영구화.

## 포맷 (Nygard + 본 프로젝트 메타데이터)

새 ADR은 [`aidlc-docs/adr/0000-template.md`](../../aidlc-docs/adr/0000-template.md)를 복제하여 작성한다.

### 필수 필드 (모든 ADR에 존재해야 함)

- `# NNNN. <Title>` — 4자리 시퀀셜 번호 + 결정 요약
- `**Date**` — YYYY-MM-DD (회고 ADR은 실제 결정일 또는 audit.md 추적일)
- `**Status**` — `Proposed` / `Accepted` / `Accepted (Retroactive)` / `Deprecated` / `Superseded by NNNN`
- `**Affects-Units**` — 영향받는 AI-DLC unit (`U07, U09, U10` 또는 `none`)
- `**Source-Evidence**` — 결정 근거 (audit.md 라인, 코드 경로, unit 산출물 등)

### 권장 필드

- `**Affects-Code**` — 워크스페이스 상대 경로 (예: `legacy-integration/domain/`)
- `**Legacy-ID**` — 이전 식별자 (예: `ADR-U13c-001`)
- `**Supersedes**` — 이 ADR이 대체하는 이전 번호
- `**Superseded-By**` — 이 ADR을 대체한 후속 번호

### 본문 구조 (Nygard)

- `## Context` — 결정 배경 (사실 위주)
- `## Decision` — 채택 결정 (단수형, 명확)
- `## Consequences` — Positive / Negative / Follow-up
- `## Alternatives Considered` — (선택) 거부한 대안 + 이유

## 카테고리 (aidlc-docs/adr/ 하위 디렉토리)

| 카테고리 | 의미 |
|---|---|
| `cross-cutting/` | 다수 unit/서비스에 걸친 결정 |
| `microservices/` | 11개 백엔드 서비스 공통/개별 |
| `frontend/` | React/Vite/ATOM DS 등 |
| `infrastructure/` | Terraform/EKS/docker/CI |
| `tmf-compliance/` | TMF 표준 waive/deviation/CTK |

## 변경 정책

- **신규**: 다음 빈 시퀀셜 번호로 ADR 신규 생성. **기존 ADR 본문을 수정해 결정을 바꾸지 않음**.
- **갱신(supersede)**: 새 ADR 작성 + 기존 ADR `Status: Superseded by NNNN` + `Superseded-By: NNNN`. 이전 본문 보존.
- **폐기(deprecate)**: 더 이상 유효하지 않으나 후속 없으면 `Status: Deprecated` + Consequences에 이유.

## ADR 작성 트리거

다음 조건 중 하나라도 해당하면 **ADR 작성 필수**:

1. 새 마이크로서비스/도메인 추가, 분할, 통합
2. 외부 표준(TMF/SID/etc.) 미준수(NC) 발생 → [ADR-0001 NC waive 정책](../../aidlc-docs/adr/tmf-compliance/0001-tmf-nc-waive-policy.md) 절차
3. 의존성 베이스라인 변경 (Spring Boot major, Java major, React major 등)
4. 인프라 토폴로지 변경 (Terraform module 추가/제거, 컴퓨팅 분리 등)
5. 데이터 권위 이전 (Strangler Fig 단계 전환 등)
6. 보안/인증 모델 변경

다음은 ADR 불필요:
- 버그 수정 (단, 수정 결정이 아키텍처에 영향 미치는 경우 예외)
- minor/patch 버전 업
- 리팩토링 (단, 도메인 경계 이동은 ADR 필요)

## 백링크 (Relates-To-ADR)

- 모든 unit `aidlc-docs/construction/{unit}/INDEX.md` 상단에 `**Relates-To-ADR**: [NNNN, NNNN]` 메타가 있어야 한다. 자세한 사항은 [`aidlc-docs-unit-conventions.md`](./aidlc-docs-unit-conventions.md#relates-to-adr-메타) 참조.
- ADR 색인 자동 생성은 [`aidlc-docs/index/adr-index.md`](../../aidlc-docs/index/adr-index.md)에 누적.

## 회고 ADR (Retroactive)

기존 구축된 결정을 회고적으로 ADR화할 때:

- `Status: Accepted (Retroactive)`
- `Date:` — 가능한 한 실제 결정일을 git log/audit.md에서 역추적하여 기재
- `Source-Evidence:`에 회고임을 명시 (예: "원본: specs/tmf/u13c/ADR-U13c-001-...")

## 자동화 (참고)

ADR 영향 분석/초안 작성/백링크 검증 자동화는 본 프로젝트의 다음 자산이 담당:

- 서브에이전트 [`adr-curator`](../agents/adr-curator.md) — 새 결정 감지 시 초안 생성/리뷰
- 서브에이전트 [`adr-impact-scanner`](../agents/adr-impact-scanner.md) — 코드 변경 시 영향 ADR 분석
- 훅 [`hooks/adr_backlink_check.py`](../hooks/adr_backlink_check.py) — unit INDEX.md 변경 시 `Relates-To-ADR` 검증

이들은 **opt-in 방식**으로 활성화되며, 기본은 비활성. 활성화 방법은 [`extensions/adr/governance/adr-governance.md`](../extensions/adr/governance/adr-governance.md) 참조.
