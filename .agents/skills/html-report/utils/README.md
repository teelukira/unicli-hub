# HTML 리포트 엔진

JSON 스펙 하나로 자체 완결형(self-contained) HTML 리포트를 생성하는 엔진.
작성자는 컴팩트한 JSON만 쓰고, 반복적인 HTML/CSS는 엔진이 전개한다 — 리포트
마크업을 손으로 작성하지 않으므로 토큰 소모가 크게 줄어든다.

## 사용법

```bash
# 렌더링
python hub/skills/html-report/utils/report_engine.py spec.json -o out.html

# 스펙 검증만 (출력 없음, 0/1 종료)
python hub/skills/html-report/utils/report_engine.py spec.json --check

# 로컬 이미지를 base64로 인라인 (단일 파일 산출물)
python hub/skills/html-report/utils/report_engine.py spec.json -o out.html --embed-assets
```

- 의존성 없음 (Python 3 stdlib만). 출력 HTML은 CSS 인라인으로 자체 완결.
- `mermaid` 컴포넌트가 있으면 그것만 런타임에 CDN을 로드한다.
- 시작점: `hub/skills/html-report/utils/examples/sample-report.json`을 복사해 편집하라
  (전체 13개 컴포넌트를 모두 행사하는 레퍼런스 스펙).

## 파일 구성

- `report_engine.py` — CLI + `ReportRenderer` (컴포넌트 디스패치)
- `theme.py` — 동결된 CSS 테마("Blueprint Dossier") + accent 팔레트
- `inline.py` — 인라인 미니 마크업 파서
- `examples/sample-report.json` — 레퍼런스 스펙

## 스펙 스키마

### 루트

```jsonc
{
  "title": "리포트 제목",          // 필수
  "subtitle": "부제",              // 선택
  "kicker": "REPORT",              // 선택, 제목 위 작은 라벨
  "lang": "ko",                    // 선택, 기본 "en"
  "accent": "blueprint",           // blueprint|teal|slate|rust|indigo
  "metadata": { "키": "값" },       // 선택, 헤더 메타 그리드
  "toc": { "variant": "sticky-horizontal", "auto": true },
  "footer": "문구" 또는 ["좌", "우"],
  "sections": [ ... ]              // 필수, 비어 있으면 안 됨
}
```

`toc.variant`: `sticky-horizontal`(상단 고정 바) | `card-vertical`(목차 카드).
`toc.auto: true`(기본)면 섹션 id/title로 자동 생성. `toc.entries`로 명시 가능.

### 섹션

```jsonc
{
  "id": "s1",                      // 선택, 없으면 sec-N 자동 생성
  "title": "섹션 제목",             // 필수
  "index": "1",                    // 선택, 없으면 순번
  "status": { "label": "PASS", "kind": "pass" },   // 선택, 헤딩 우측 배지
  "components": [ ... ],
  "subsections": [ { "id", "title", "components" } ]
}
```

### 컴포넌트 (`{"type": "..."}`)

| type | 핵심 필드 |
|------|-----------|
| `text` | `value`: 문자열 또는 문자열 배열(여러 문단) |
| `stat_grid` | `cards`: `[{value, label, color}]` — color: green\|red\|yellow\|blue\|gray\|purple |
| `table` | `columns`: `[{key, label, align}]`, `rows`: 아래 참조, `caption` |
| `progress_list` | `items`: `[{label, value(0~100), text, color}]` — color: green\|red\|yellow\|blue |
| `badge` | `items`: `[{text, kind}]` — 독립 배지 행 |
| `legend` | `items`: `[{color, label}]` — color: 이름 또는 `#hex` |
| `status_grid` | `items`: `[{status, name, meta}]` — status: up\|down\|warn |
| `callout` | `severity`: info\|warn\|error\|success\|gap, `title`, `body`, `label` |
| `code_block` | `language`, `code` |
| `mermaid` | `diagram`: Mermaid 소스 (이스케이프 안 함, `<script>` 금지) |
| `details` | `summary`, `open`(bool), `components`: `[...]` |
| `image_grid` | `images`: `[{src, caption}]` |

### 테이블 행

```jsonc
// 그룹 구분 행 (colspan 밴드)
{ "kind": "group", "label": "`im_eqp_bas` → resource-inventory" }

// 데이터 행 — cells 키는 columns의 key와 일치
{ "cells": {
    "col1": "문자열 셀 (인라인 마크업 지원)",
    "col2": { "text": "객체 셀", "color": "red", "align": "center" }
}}
```

셀 값은 문자열(인라인 마크업) 또는 `{text, color, align}` 객체.
`color`: red\|green\|amber\|blue\|gray. `align`: center\|right.

## 인라인 미니 마크업

`text`, 테이블 셀, `callout` 본문, 메타값 등 텍스트 필드에서 사용:

| 마크업 | 결과 |
|--------|------|
| `` `code` `` | `<code>` |
| `**bold**` | 굵게 |
| `~small~` | 작은 글씨 |
| `[badge:KIND]텍스트[/]` | 색상 배지 |
| `[c:COLOR]텍스트[/]` | 색상 강조 (red\|green\|amber\|blue\|gray) |
| `[link:#id]텍스트[/]` | 앵커 링크 (`#` 내부 앵커만) |
| `\n` | 줄바꿈 `<br>` |

배지 KIND: `pass fail warn info success error skip new gap` +
도메인 `resource catalog geo ipam zone party logical`.

모든 텍스트는 먼저 HTML 이스케이프되며, 위 화이트리스트 마커만 태그를
재주입한다 — 추출/레거시 데이터에서 와도 안전하다.

## 도메인 생성기에서 엔진 호출

`build_imown_sid_pg_lineage_report.py`처럼 데이터에서 스펙을 프로그램으로 만드는
생성기는 엔진을 직접 import 해서 쓴다:

```python
import sys
from pathlib import Path
UTILS = Path(__file__).resolve().parents[N] / "hub" / "skills" / "html-report" / "utils"
sys.path.insert(0, str(UTILS))
from report_engine import ReportRenderer

spec = build_spec(...)            # dict 조립
html = ReportRenderer(spec).render()
Path("out.html").write_text(html, encoding="utf-8")
```
