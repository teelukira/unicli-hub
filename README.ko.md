# UniCLI-Hub

UniCLI-Hub는 여러 AI CLI 설정을 하나의 원본에서 관리하고 각 도구별 위치로 fanout하는 목업/참조 프레임워크입니다.

이 저장소는 애플리케이션 프로젝트가 아닙니다. 고객사, 제품, 납품 워크스트림 같은 특정 프로젝트 컨텍스트를 담지 않습니다. 목적은 에이전트, 스킬, 훅, MCP 서버, 메모리, 진입 문서를 여러 AI CLI에 일관되게 배포하는 구조를 유지하고 검증하는 것입니다.

영문 문서는 [README.md](./README.md)를 참고하세요.

## 이 프레임워크가 하는 일

UniCLI-Hub는 `hub/`를 단일 원본으로 보고 도구별 생성 파일을 만듭니다.

| 자산 | 원본 | 생성 대상 |
|---|---|---|
| 진입 문서 | `.unicli-hub/templates/*.tmpl`, `hub/memory/`, `hub/project-context.md` | `AGENTS.md`, `CLAUDE.md` |
| 에이전트 | `hub/agents/` | `.claude/agents/`, `.cursor/agents/`, `.agents/`, `.kiro/agents/`, `.codex/agents/`, `.grok/agents/` |
| 스킬 | `hub/skills/` | `.claude/skills/`, `.cursor/skills/`, `.agents/skills/`, `.kiro/skills/`, `.grok/skills/` |
| 훅 | `hub/hooks/`, `hub/registry/hook-events.json` | `.claude/settings.json`, `.cursor/hooks.json`, `.agents/settings.json`, `.grok/hooks/unicli-hub.json` |
| MCP 서버 | `hub/mcp-servers.json` | `.mcp.json`, `.cursor/mcp.json`, `.agents/mcp_config.json`, `.kiro/settings/mcp.json`, `.codex/config.toml`, `.grok/config.toml` |
| 메모리 | `hub/memory/*.md` | 생성된 진입 문서에 포함 |

## 지원 CLI

| CLI | 생성 경로 | 진입점 |
|---|---|---|
| Antigravity / agy | `.agents/` | `AGENTS.md` |
| Claude Code | `.claude/` | `CLAUDE.md` |
| Cursor | `.cursor/` | `AGENTS.md` 및 Cursor 파일 |
| Kiro | `.kiro/` | 생성된 steering 및 agent 파일 |
| OpenAI Codex | `.codex/` | `AGENTS.md` 및 agent/skill 파일 |
| Grok Build | `.grok/` | `AGENTS.md` 및 `.grok/` agent, skill, hook, MCP 파일 |

## 도구별 기능 지원 (스킬, 서브에이전트, MCP)

AI CLI마다 확장 기능을 지원하는 방식이 다릅니다. 프레임워크가 이 차이를 추상화하여 배포하지만, 각 도구의 동작 방식을 이해하는 것이 좋습니다.

### 1. 구글 안티그래비티 (Google Antigravity, agy)
- **스킬 (Skills)**: 커스텀 폴더 구조(`.agents/skills/<skill_name>/SKILL.md`)를 통해 네이티브하게 스킬을 로드하고 스캔합니다.
- **서브에이전트 (Subagents)**: 정적 파일로 커스텀 에이전트를 정의하는 대신, 내장 에이전트(예: `research`, `self`)를 제공하며 런타임에 `define_subagent` 도구를 호출하여 동적으로 에이전트를 생성하는 방식을 사용합니다.
- **MCP**: 워크스페이스 MCP는 `.agents/mcp_config.json` (`mcpServers`)입니다. 전역 설정은 `~/.gemini/config/mcp_config.json`입니다.

### 2. 커서 (Cursor)
- **스킬 (Skills)**: `.cursor/skills/<skill_name>/SKILL.md` 네이티브 Agent Skills입니다. 호환을 위해 `.agents/skills/`와 Claude/Codex 스킬 디렉터리도 읽습니다. 항상 적용되는 프로젝트 룰은 `.cursor/rules/*.mdc`입니다.
- **서브에이전트 (Subagents)**: `.cursor/agents/*.md` 마크다운과 YAML 프론트매터(`name`, `description`, `model`, `readonly`, `is_background`).
- **MCP**: 프로젝트 `.cursor/mcp.json`.

### 3. 클로드 코드 (Claude Code)
- **스킬 (Skills)**: `.claude/skills/<skill_name>/SKILL.md`.
- **서브에이전트 (Subagents)**: `.claude/agents/*.md` 마크다운과 YAML 프론트매터(`name`, `description`, 선택 `tools`, `sonnet` 같은 모델 alias).
- **MCP**: 프로젝트 최상단 `.mcp.json`.

### 4. 그록 빌드 (Grok Build)
- **스킬 (Skills)**: `.grok/skills/<skill_name>/SKILL.md`에 네이티브 프로젝트 스킬을 둡니다. Grok은 호환 설정으로 Claude, Cursor, Antigravity 스킬 디렉터리도 스캔할 수 있지만, 이름이 겹치면 `.grok/skills/`가 이깁니다.
- **서브에이전트 (Subagents)**: `.grok/agents/*.md` 마크다운과 YAML 프론트매터(`name`, `description`, `model`, `permission_mode`)로 정의합니다. 런타임에 `spawn_subagent`로 실행됩니다.
- **MCP**: 프로젝트 범위 TOML인 `.grok/config.toml`의 `[mcp_servers.<name>]`으로 구성합니다. 네이티브 Grok 설정이 Claude, Cursor, `.mcp.json` 호환 소스보다 우선합니다.
- **Trust**: 프로젝트 `.grok/hooks/`와 repo-local MCP는 폴더를 trust한 뒤에만 동작합니다 (`/hooks-trust` 또는 `grok --trust`).

### 5. 오픈AI 코덱스 (OpenAI Codex)
- **스킬 (Skills)**: 저장소 스킬은 `.agents/skills/<skill_name>/SKILL.md`입니다 (Antigravity와 공유하는 Agent Skills 위치). 사용자 스킬은 `$HOME/.agents/skills`입니다.
- **서브에이전트 (Subagents)**: 프로젝트 커스텀 에이전트는 `.codex/agents/*.toml`이며 `name`, `description`, `developer_instructions`가 필요합니다.
- **MCP**: 프로젝트 `.codex/config.toml`의 `[mcp_servers.<name>]`.

### 6. 키로 (Kiro)
- **스킬 (Skills)**: `.kiro/skills/<skill_name>/SKILL.md` 네이티브 Agent Skills입니다. `.kiro/steering/`은 항상 적용되는 프로젝트 컨텍스트이며 스킬이 아닙니다.
- **서브에이전트 (Subagents)**: `.kiro/agents/*.json` (JSON은 계속 유효, `prompt`와 `read`/`write`/`shell` 태그형 `tools`).
- **훅 (Hooks)**: `.kiro/hooks/unicli-hub.json` (`version: v1`, PascalCase 트리거).
- **MCP**: `.kiro/settings/mcp.json`.

## 저장소 구조

```text
.
├── hub/                    # 프레임워크 원본
│   ├── registry/           # fanout, hook-event, model-profile 원장
│   ├── agents/             # 선택적 에이전트 프롬프트 원본
│   ├── skills/             # 선택적 스킬 원본
│   ├── hooks/              # CLI 공통 훅 스크립트
│   ├── memory/             # 진입 문서에 들어갈 메모리 조각
│   ├── common/             # 프레임워크 참조 문서
│   ├── mcp-servers.json    # MCP 서버 원장
│   └── project-context.md  # 다음 작업자가 볼 프레임워크 컨텍스트
├── .unicli-hub/            # 렌더러 구현 및 템플릿
│   ├── scripts/            # render_agents/render_skills/render_hooks/render_mcp/render_templates
│   └── templates/          # AGENTS.md 및 CLAUDE.md 템플릿
├── sync.py                 # 전체 재생성 명령 (Windows/POSIX)
├── sync.sh                 # sync.py POSIX 래퍼
├── AGENTS.md               # 생성물
└── CLAUDE.md               # 생성물
```

## 작업 규칙

수정은 `hub/` 또는 `.unicli-hub/templates/`의 원본에 합니다.

`AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.agents/`, `.kiro/`, `.codex/`, `.grok/`, `.mcp.json` 및 생성된 MCP/config 파일은 직접 수정하지 않습니다. 생성 파일 가드가 직접 수정을 차단하고 원본 위치를 안내합니다.

원본을 바꾼 뒤에는 다음을 실행합니다.

```bash
python sync.py --fix
python sync.py --check
```

POSIX에서는 `./sync.sh --fix`가 동일합니다. `--fix`는 생성물을 갱신하고 더 이상 원본이 없는 stale agent/skill을 삭제합니다. `--check`는 생성물이 원본과 어긋나면 실패합니다. 생성된 훅과 MCP launcher가 시작하려면 `python`이 PATH에 있어야 합니다.

## 현재 기준선

이 프레임워크는 의도적으로 범용 상태를 유지합니다. 현재 남기는 항목은 다음과 같습니다.

- registry 기반 agent, skill, hook, static copy, MCP, entry template fanout 렌더러
- 생성 파일 직접 수정 방지 훅
- MCP 전파 구조
- 범용 예시 스킬 1개: `html-report`
- project facts, conventions, glossary 메모리 placeholder

현재 기준선에서 제외하는 항목은 다음과 같습니다.

- 특정 방법론 전용 라이프사이클 워크플로우
- 고객사/제품 전용 에이전트와 스킬
- 특정 이슈 트래커나 코드 저장소에 묶인 납품 게이트 정책
- 도메인 전용 컨텍스트

## 콘텐츠 추가 방법

에이전트를 추가하려면 `hub/agents/`에 원본을 넣고, 필요한 경우 `hub/registry/agent-profiles.json`에 모델 프로필을 추가한 뒤 `python sync.py --fix`를 실행합니다.

스킬을 추가하려면 `hub/skills/<skill-name>/SKILL.md`를 만듭니다. 필요한 보조 파일은 같은 폴더 아래에 둘 수 있습니다. 스킬 렌더러가 폴더 내용과 reference 파일을 지원 대상에 복사합니다.

MCP 서버를 추가/삭제하려면 `hub/mcp-servers.json`을 수정합니다. 비밀값은 파일에 넣지 말고 상속 환경변수나 자격증명 검증용 wrapper script를 사용합니다.

모든 stdio MCP 서버는 생성 시 `scripts/mcp/run-with-env.sh`를 거칩니다. 생성된 launcher는 worktree 내부 어느 디렉터리에서 시작해도 활성 Git worktree를 찾고, **부모 프로세스 > 현재 worktree `.env.local` > 현재 worktree `.env` > primary worktree `.env.local` > primary worktree `.env`** 순서로 환경을 적용합니다. 따라서 primary worktree에는 공유 로컬 기본값을 두고 linked worktree에서 작업별 값을 덮어쓸 수 있습니다. 이 동작을 우회해야 하는 서버만 `"_project_env": false`를 지정합니다.

생성되는 진입 문서 문구를 바꾸려면 `.unicli-hub/templates/AGENTS.md.tmpl` 또는 `.unicli-hub/templates/CLAUDE.md.tmpl`을 수정합니다.

## Registry 파일

- `hub/registry/hook-events.json`: 논리 훅 이벤트를 각 CLI의 이벤트명으로 매핑합니다.
- `hub/registry/fanout.json`: agent, skill, static copy의 source/target 경로와 orphan 정책을 선언합니다.
- `hub/registry/agent-profiles.json`: 생성되는 Codex subagent prompt의 모델 메타데이터를 저장합니다.
