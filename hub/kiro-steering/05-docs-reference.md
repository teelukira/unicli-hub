---
inclusion: manual
---

# 기획서 산출물 참조 가이드

## docs/ 디렉토리 산출물 매핑

코드 구현 시 아래 문서들을 참조하세요:

| 파일 | 내용 | 관련 Unit |
|------|------|-----------|
| `docs/00_index.md` | 프로젝트 전체 개요 | 전체 |
| `docs/01_r00-as-is-시스템-분석-종합.md` | AS-IS 분석 (95기능, 600+API) | U07 |
| `docs/02_r01-to-be-아키텍처-설계서.md` | C4 아키텍처, 25개 ODA 컴포넌트 | 전체 |
| `docs/03_r02-도메인별-bpm-설계서.md` | 12개 BPMN 프로세스 | U04 |
| `docs/05_r03-기능-정의서-oda-기반.md` | ODA 기반 기능 정의 | 전체 |
| `docs/06_r05-통합-데이터-모델-sid-기반.md` | SID 기반 데이터 모델 | U02, U03 |
| `docs/07_r06-uiux-설계서.md` | React UI, 70+ 화면 | U11 |
| `docs/08_r07-as-is-시스템-전환-계획서.md` | Strangler Fig 전환 전략 | U07 |
| `docs/09_r08-bpm-플랫폼-설계서.md` | Camunda 8 상세 설계 | U04 |
| `docs/10_r09-레거시-인터페이스-정의서.md` | TIO/iSigma/CMS Bus/FTP 명세 | U07 |
| `docs/11_r10-보안-아키텍처-설계서.md` | Zero Trust 보안 설계 | U01, U12 |
| `docs/12_r11-skt-tmfc-컴포넌트-카탈로그.md` | SKT 고유 18개 컴포넌트 | 전체 |
| `docs/13_r12-프로세스-갭-분석-레포트.md` | eTOM 갭 분석 (매핑률 72%) | 전체 |
| `docs/14_r13-마이그레이션-로드맵.md` | 3 Phase 로드맵 (2026-2028) | 전체 |

## docs/raw/ TMF 바이너리 원본 (PDF/Excel)

| 경로 | 내용 | 관련 Unit |
|------|------|-----------|
| `docs/raw/openapi/TMF639_*.pdf` | Resource Inventory API | U02 |
| `docs/raw/openapi/TMF634_*.pdf` | Resource Catalog API | U03 |
| `docs/raw/openapi/TMF641_*.pdf` | Service Ordering API | U04 |
| `docs/raw/openapi/TMF642_*.pdf` | Alarm Management API | U06 |
| `docs/raw/openapi/TMF702_*.pdf` | Resource Activation API | U04 |
| `docs/raw/openapi/TMF621_*.pdf` | Trouble Ticket API | U06 |
| `docs/raw/etom/` | eTOM GB921 Suite v25.0 (PDF/Excel) | 전체 |
| `docs/raw/sid/` | SID GB922 v25.0 (Excel/UML) | 전체 |
| `docs/raw/oda/` | ODA GB998, IG1171, IG1242 (PDF) | 전체 |

## docs/tmf-oracle/ TMF Knowledge Oracle (파싱된 .md)

`tmf-knowledge-ingest` 에이전트가 raw/ 바이너리를 파싱하여 규격단위 .md 청크로 저장하는 디렉토리.

| 경로 | 내용 |
|------|------|
| `docs/tmf-oracle/openapi/tmfNNN/` | Open API 규격별 청크 |
| `docs/tmf-oracle/etom/` | eTOM 프로세스 프레임워크 청크 |
| `docs/tmf-oracle/sid/` | SID 정보 프레임워크 청크 |
| `docs/tmf-oracle/oda/` | ODA 컴포넌트 아키텍처 청크 |

## docs/research/ 리서치 결과

`aidlc-researcher` 에이전트가 조사한 기술 리서치 결과가 저장되는 디렉토리.
파일 명명: `docs/research/{unit-id}-{topic-slug}.md`

## aidlc-docs/ AI-DLC 산출물

| 경로 | 내용 |
|------|------|
| `aidlc-docs/inception/requirements/` | 요구사항 분석 |
| `aidlc-docs/inception/plans/` | 실행 계획 |
| `aidlc-docs/construction/u01-infra-foundation/` | U01 인프라 설계 산출물 |
| `aidlc-docs/construction/u01-db-foundation/` | U01-DB 데이터베이스 설계 산출물 |
| `aidlc-docs/aidlc-state.md` | 전체 진행 상태 |
| `aidlc-docs/audit.md` | 감사 로그 |
