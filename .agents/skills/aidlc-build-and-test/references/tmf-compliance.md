# TMF Compliance — Reference Pointer

Read `hub/extensions/tmf/compliance/tmf-compliance.md` for the full 14-rule TMF compliance matrix (TMF-A through TMF-N). Load this file ONLY when TMF Compliance extension is Enabled.

Rules TMF-A/B/C/D/E/F/G/H/I/J/K/L/M/N are detailed there.

Key summary (TMF-A through TMF-N — 14 rules):
- TMF-A: Prerequisite Artifacts (api-spec.yaml, component-mapping.md, sid-mapping.md 등)
- TMF-B: OpenAPI Schema Fidelity (SID GB922 속성·타입 정합)
- TMF-C: OpenAPI Endpoints & HTTP Contract (GET/POST/PATCH/DELETE semantics, 응답 코드)
- TMF-D: OpenAPI Pagination & Filter (totalResults/totalPages/offset/limit, fieldsParam)
- TMF-E: OpenAPI Error Contract (400/404/422/500 schema)
- TMF-F: SID Entity Naming & SSoT (@type, DB 테이블명, 도메인 모델 정합)
- TMF-G: SID Attribute Fidelity (MODA 25.5 기준 SID 속성 망라 여부)
- TMF-H: eTOM Lifecycle State Machine (eTOM 4-state/8-state 전이 검증)
- TMF-I: TMF Event Pattern Hub/Notification — **3-tier (U47)**: Tier 1 이벤트 클래스 정의, Tier 2 퍼블리셔 포트 주입(wiring), Tier 3 핸들러 publish() 호출 + lifecycleStatus 분기(trigger)
- TMF-J: SKT Extension Isolation (skt_ 접두사 분리, @type 네임스페이스)
- TMF-K: ODA Component Mapping (IG1242 v24 TMFC ID, Exposed/Internal Functions)
- TMF-L: ODA Functional Framework Alignment (GB1033 v25.5 도메인·기능블록)
- TMF-M: ODA Canvas/CRD Compliance (조건부 — Canvas 배포 시만 적용)
- TMF-N: TMF API Directory Registration (버전·상태 Production 확인)

The tmf-compliance-reviewer subagent uses the atom-tmf-kb-mcp tools to verify each rule.
