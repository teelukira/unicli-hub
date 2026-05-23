---
name: html-report
description: "JSON 스펙으로 자체 완결형 HTML 리포트를 생성합니다. QA 리포트, 데이터 매핑 리포트, 감사 요약, 대시보드 등 독립 HTML 문서를 만들 때 사용합니다."
---

# HTML 리포트 생성

JSON 스펙 하나로 폴리시된 자체 완결형 HTML 리포트를 만든다. 엔진은
`hub/skills/html-report/utils/report_engine.py`이며 "Blueprint Dossier" 테마가 동결돼 있다.

## 사용 시점

- QA/테스트 리포트, 데이터 매핑·적재 리포트, 감사 요약, 운영 대시보드 등
  **독립 실행형 HTML 문서**를 생성할 때.
- 손으로 작성된 기존 HTML을 부분 편집할 때는 사용하지 않는다.

## 왜 스킬인가 (토큰 절감)

리포트 HTML/CSS를 직접 작성하면 수백 줄의 반복 마크업에 토큰을 소모한다.
대신 **컴팩트한 JSON 스펙만 작성**하고 파이썬 엔진이 HTML/CSS를 전개한다.
리포트 마크업을 절대 손으로 쓰지 말 것.

## 워크플로

1. 리포트에 담을 데이터/결과를 수집한다.
2. JSON 스펙 파일을 작성한다. 스키마는 `hub/skills/html-report/utils/README.md`,
   전체 컴포넌트를 행사하는 예시는 `hub/skills/html-report/utils/examples/sample-report.json`.
3. 렌더링: `python hub/skills/html-report/utils/report_engine.py spec.json -o out.html`
4. 검증: `python hub/skills/html-report/utils/report_engine.py spec.json --check`
5. 시각 확인: 브라우저로 열거나 Playwright 플러그인으로 스크린샷.

## 컴포넌트 치트시트

루트: `{title, subtitle, kicker?, accent?, metadata?, toc?, footer?, sections[]}`
섹션: `{id?, title, index?, status?, components[], subsections?}`

컴포넌트 `{"type": ...}` — 13종:

| type | 핵심 필드 |
|------|-----------|
| `text` | `value` (문자열/배열) |
| `stat_grid` | `cards:[{value,label,color}]` |
| `table` | `columns:[{key,label,align}]`, `rows:[...]` |
| `progress_list` | `items:[{label,value,text,color}]` |
| `badge` | `items:[{text,kind}]` |
| `legend` | `items:[{color,label}]` |
| `status_grid` | `items:[{status,name,meta}]` (status: up/down/warn) |
| `callout` | `severity` (info/warn/error/success/gap), `title?`, `body` |
| `code_block` | `language?`, `code` |
| `mermaid` | `diagram` |
| `details` | `summary`, `open?`, `components[]` |
| `image_grid` | `images:[{src,caption}]` |
| `raw_html` | `html` (스키마 표현 불가 시 탈출구) |

테이블 행: 데이터 행 `{cells:{key:값}}` 또는 그룹 행 `{kind:"group",label:...}`.
셀 값은 문자열 또는 `{text,color,align}`.

## 인라인 마크업 (텍스트·셀·콜아웃 본문 공용)

`` `code` `` · `**bold**` · `~small~` · `[badge:KIND]x[/]` ·
`[c:red|green|amber|blue|gray]x[/]` · `[link:#id]x[/]` · `\n`→줄바꿈.

## 참고

- 데이터에서 스펙을 프로그램으로 만드는 도메인 생성기는 엔진을 직접
  import 한다 (`hub/skills/html-report/utils/README.md`의 마지막 절 참조).
- 이 스킬 파일을 수정한 뒤에는 `./sync.sh --fix`로
  파생 디렉토리에 전파한다.

