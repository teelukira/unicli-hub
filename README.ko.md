# UniCLI-Hub: AI 유목민을 위한 통합 워크스페이스

> *(회사가 도구를 안 사주나요? 저희가 도와드립니다.)*

**UniCLI-Hub**는 AI 구독 피로와 컨텍스트 파편화에 지친 개발자들을 위한 중앙 집중식 **SSOT (Single Source of Truth) 프레임워크**입니다.

## 문제: 구독 피로와 컨텍스트 파편화

AI 도구들은 훌륭하지만, 모든 도구에 매달 $20씩 지불하는 것은 부담스럽습니다. 할당량(Rate Limit)을 피하기 위해 여러 AI CLI(Claude, Gemini, Cursor 등)의 무료 티어를 오가다 보면, 커스텀 스킬, 에이전트 설정, 프로젝트 메모리가 도구마다 흩어져 AI의 "두뇌"가 파편화됩니다.

## 해결책: 모든 도구를 지배하는 단 하나의 허브

**UniCLI-Hub**는 **에이전트, 스킬, 훅, MCP 서버** 설정을 단일 디렉토리에 중앙 집중화합니다. 이 자산들은 지원되는 모든 CLI 도구로 자동 배포(Fan-out)되어, 현재 어떤 도구를 사용하든 동일한 컨텍스트와 기능을 유지할 수 있게 합니다.

**UniCLI-Hub와 함께라면:**
- **끊김 없는 전환:** Claude 토큰이 다 떨어졌나요? 아키텍처를 다시 설명할 필요 없이 Gemini나 Antigravity(agy)로 즉시 전환하세요.
- **통합 메모리:** 프로젝트 사실 관계, 컨벤션, 용어집을 모든 도구가 공유합니다.
- **자동화된 도구 연동:** MCP 서버 정의와 훅 로직을 한 곳에서 관리합니다.
- **비용 절감:** 여러 무료 티어를 하나의 "Pro" 경험처럼 활용하여 생산성을 극대화하세요.

---

## 지원되는 CLI

| CLI | 파생 경로 | 진입점 (Entry Point) |
|-----|------------------|-------------|
| **Antigravity (agy)** | `.agy/` | `AGY.md` |
| **Claude Code** | `.claude/` | `CLAUDE.md` |
| **Gemini CLI** | `.gemini/` | `GEMINI.md` |
| **Cursor** | `.cursor/` | `.cursor/rules/*.mdc` |
| **Kiro** | `.kiro/` | `.kiro/steering/*.md` |
| **OpenAI Codex** | `.codex/` | `AGENTS.md` |

---

## 빠른 시작

```bash
# 1) 프레임워크 클론
git clone <this-repo> my-project && cd my-project

# 2) hub/ 디렉토리에서 SSOT 소스 수정
#    - hub/project-context.md
#    - hub/memory/project-facts.md
#    - hub/mcp-servers.json

# 3) 모든 CLI 타겟 동기화
./sync.sh --fix

# 4) 원하는 도구 실행
agy                   # Antigravity CLI
claude                # Claude Code
gemini                # Gemini CLI
cursor .              # Cursor
```

---

## 프레임워크 구조

UniCLI-Hub는 **프레임워크 코어**와 **프로젝트 데이터**를 분리하여 관리합니다.

### 1. 허브 (`hub/`) — 당신의 데이터
**Single Source of Truth**가 정의되는 곳입니다. **이곳의 파일들을 수정하세요.**
- `hub/agents/`: 공통 및 특화 에이전트의 원본 프롬프트.
- `hub/skills/`: 커스텀 스킬 (마크다운 + 참조 자료).
- `hub/hooks/`: 공유 Python 훅 로직.
- `hub/memory/`: 프로젝트 사실 관계, 컨벤션, 용어집.
- `hub/mcp-servers.json`: 통합 MCP 설정.
- `hub/project-context.md`: 프로젝트의 전체적인 맥락.

### 2. 코어 (`.unicli-hub/`) — 프레임워크 로직
자산을 배포하기 위한 내부 로직입니다. 일반적으로 수정할 필요가 없습니다.
- `scripts/`: 에이전트, 스킬, 훅, MCP, 템플릿용 Python 렌더러.
- `templates/`: CLI별 진입점 템플릿 (`CLAUDE.md.tmpl` 등).

### 3. 파생 타겟 (자동 생성)
**직접 수정하지 마세요.** `./sync.sh`에 의해 관리됩니다.
- 루트: `CLAUDE.md`, `GEMINI.md`, `AGY.md`, `AGENTS.md`.
- 도구 디렉토리: `.claude/`, `.gemini/`, `.cursor/`, `.kiro/`, `.codex/`, `.agy/`.

---

## 대원칙: 한 곳에서 수정하고 모든 곳에서 동기화

1.  `hub/` 하위의 소스를 수정합니다.
2.  `./sync.sh --fix`를 실행합니다.
3.  프레임워크의 **Python 가드**(`generated_file_guard.py`)가 파생 파일에 대한 직접 수정을 차단하고 `hub/`로 안내합니다.

---

## 주요 기능

### 통합 MCP 설정
`hub/mcp-servers.json`에서 도구(Tavily, JIRA, GitLab 등)를 정의하세요. `./sync.sh`를 실행하면 모든 CLI에 설정이 배포되며, Gemini와 Antigravity의 `allowed` 리스트도 자동으로 업데이트됩니다.

### 특화 에이전트 추가
`hub/agents/`에 마크다운 프롬프트와 `.kiro.json` 메타데이터를 추가하면, 프레임워크가 모든 플랫폼에 맞는 에이전트를 자동으로 생성합니다.

---

## CI 연동

`.pre-commit-config.yaml`이 포함되어 있습니다. 커밋 시 파생 파일이 소스와 어긋나지 않도록 설정하세요:
```bash
pre-commit install
```
이제 모든 커밋 전에 `./sync.sh --check`가 실행됩니다.

---

*UniCLI-Hub: 모든 도구를 지배하는 단 하나의 허브.*
