# UniCLI-Hub: 짠돌이 AI 유목민을 위한 워크스페이스

> *(회사가 AI 툴 비용을 안 대준다고요? 저희가 해결해드릴게요.)*

**UniCLI-Hub**는 AI 구독료 피로에 지친 개발자를 위한 **통합 컨텍스트 관리 워크스페이스**입니다.

## 왜 만들었나 ("가난한 개발자" 문제)

솔직해지죠. AI 도구는 훌륭하지만 모두에게 월 20달러씩 내는 건 다른 얘기입니다. 회사가 AI 도구를 지원해주지 않거나, Gemini·Claude Code·Cursor·Kiro-CLI의 무료 티어를 제정신으로 최대한 활용하고 싶을 수 있습니다.

토큰 한도를 피하려고 여러 AI CLI의 Free/Basic 티어를 계속 갈아타다 보면, AI의 "뇌"가 조각납니다. `agent.md`는 여기, 커스텀 스킬은 저기, 프로젝트 컨텍스트는 매번 다시 설명해야 하죠.

## 해결책

**UniCLI-Hub**는 AI 워크플로우의 **Single Source of Truth (SSOT)** 역할을 합니다. 서브에이전트·메모리·스킬을 한 곳에 모아, 토큰 한도에 걸리는 순간 다른 도구로 매끄럽게 전환할 수 있게 합니다.

**UniCLI-Hub로 할 수 있는 일:**

- **Claude 토큰이 떨어졌다?** 프로젝트 아키텍처를 다시 설명하지 않고 Gemini CLI로 바로 전환.
- **통합 메모리 유지:** `.cursorrules`, Kiro 시스템 프롬프트, Claude 컨텍스트를 한 디렉토리에서 공유.
- **비용 절감:** 무료 티어 조합과 단일 구독만으로 "Pro" 경험을 유지.

> English version: [README.md](./README.md)

---

## 지원 CLI

| CLI | 파생 위치 | 진입점 |
|-----|-----------|--------|
| Claude Code | `.claude/` | `CLAUDE.md` |
| Cursor | `.cursor/rules/`, `.cursor/agents/` | `.cursor/rules/*.mdc` |
| Gemini CLI | `.gemini/` | `.gemini/GEMINI.md` |
| Kiro | `.kiro/steering/`, `.kiro/agents/` | `.kiro/steering/*.md` |
| OpenAI Codex | `.codex/`, `AGENTS.md` | `AGENTS.md` (루트) |

## Quick Start

```bash
# 1) 템플릿 복제 (또는 이 디렉토리를 시작점으로)
git clone <this-repo> my-project && cd my-project

# 2) 프로젝트에 맞게 원천 파일 편집
#    - .unicli-rules/project-context.md
#    - .unicli-rules/memory/project-facts.md
#    - .unicli-rules/memory/conventions.md
#    - .unicli-rules/memory/glossary.md

# 3) 모든 CLI의 파생 파일 재생성
./.unicli-rules/sync.sh --fix

# 4) 원하는 CLI로 열기
claude                # Claude Code
cursor .              # Cursor
gemini                # Gemini CLI
kiro                  # Kiro
codex                 # Codex (AGENTS.md 자동 로드)
```

## Canonical vs Derived

**편집해야 할 파일** (`.unicli-rules/`):

```
.unicli-rules/
├── core-workflow.md          # 도구 중립 워크플로우
├── project-context.md        # 프로젝트 컨텍스트
├── agents/{researcher,codegen,reviewer}.md
├── skills/{scaffold-module,run-tests}.md
├── memory/{project-facts,conventions,glossary}.md
├── common/{tool-matrix,approval-gates}.md
├── templates/
│   ├── CLAUDE.md.tmpl
│   ├── GEMINI.md.tmpl
│   ├── AGENTS.md.tmpl
│   └── frontmatter/*.yaml
├── hooks/
│   ├── generated_file_guard.py   # PreToolUse  — 파생 파일 직접 편집 차단
│   └── auto_sync.py              # PostToolUse — canonical 편집 시 sync.sh 자동 실행
└── sync.sh
```

**편집 금지 (자동 생성)**:

- `CLAUDE.md`, `AGENTS.md` (루트)
- `.claude/agents/*.md`
- `.cursor/rules/*.mdc`, `.cursor/agents/*.md`, `.cursor/skills/*`
- `.gemini/GEMINI.md`, `.gemini/agents/*.md`, `.gemini/skills/*`
- `.kiro/steering/*.md`, `.kiro/agents/prompts/*` (symlink)
- `.codex/prompts/*.md`

에이전트가 이런 파일을 직접 수정하려 하면 `generated_file_guard.py` PreToolUse 훅이 차단하고, 대신 편집해야 할 canonical 경로를 알려줍니다.

## 규칙: `sync.sh`만이 파생 디렉토리를 건드린다

- **`./.unicli-rules/sync.sh`**를 통한 수정만이 `.cursor/`, `.claude/`, `.gemini/`, `.kiro/`, `.codex/` 에 쓰기를 허용합니다.
- 그 외 경로로 (에이전트든 수동이든) 쓰는 모든 시도는 Python guard 훅이 차단합니다.
- 에이전트 프롬프트·스킬·메모리를 바꾸고 싶다면 `.unicli-rules/`에서 편집하고 `sync.sh --fix`를 실행하세요. 이 한 가지 워크플로우만 있으면 됩니다.

## 새 에이전트 추가

```bash
# 1) canonical 프롬프트 작성
cat > .unicli-rules/agents/security-scanner.md <<'EOF'
# Security Scanner Agent
...
EOF

# 2) sync.sh의 SHARED_AGENTS 배열에 이름 추가
#    (description, tool allowlist, model도 함께 지정)

# 3) 재생성
./.unicli-rules/sync.sh --fix
```

## 새 스킬 추가

`.unicli-rules/skills/<name>.md`만 만들면 sync가 Gemini·Cursor로 자동 배포합니다.

## 메모리 편집

1. `.unicli-rules/memory/*.md` 편집
2. `./.unicli-rules/sync.sh --fix`
3. CLI 세션 재시작(또는 새 스레드)하면 반영

## 훅 (Python)

| Hook | 트리거 | 동작 |
|------|--------|------|
| `generated_file_guard.py` | PreToolUse (Edit / Write) | 파생 파일 직접 편집을 차단하고, 편집해야 할 canonical 경로를 출력 |
| `auto_sync.py` | PostToolUse (Edit / Write) | `.unicli-rules/**` 수정 감지 시 `sync.sh --fix` 자동 실행 |

훅은 **순수 Python(표준 라이브러리만)**, Python 3.8+ 호환입니다. 5개 CLI의 훅 설정(`.claude/settings.local.json`, `.cursor/hooks.json`, `.gemini/settings.json`, `.kiro/hooks/*.kiro.hook`)이 모두 `python3`로 호출합니다.

## Codex 프롬프트 설치

Codex는 `~/.codex/prompts/`의 프롬프트만 slash command로 노출합니다. 설치 명령:

```bash
./.unicli-rules/sync.sh --install-codex-prompts
# → /unicli-researcher, /unicli-codegen, /unicli-reviewer
```

## CI 통합

`.github/workflows/sync-check.yml` 예시:

```yaml
name: unicli-hub sync check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./.unicli-rules/sync.sh --check
```

`sync.sh --check`은 파생 파일이 canonical과 drift가 있을 때 종료 코드 1을 반환하므로, `--fix`를 잊고 PR을 올리면 CI가 실패합니다.

## Rate Limit 피하기 (2026년 4월 기준)

모든 AI CLI는 무료/$20 티어 사용량을 빡빡하게 제한하고, **그 제한은 각 벤더마다 독립적**입니다. UniCLI-Hub가 존재하는 이유가 바로 이것 — canonical 컨텍스트 하나를 5개 CLI에 공유해, 한 도구에서 벽에 부딪히면 즉시 다른 도구로 넘어가도록 만듭니다.

### 무료 vs. $20/월 티어 — 한눈에 비교

| CLI | 무료 티어 | $20/월 유료 티어 | 비고 |
|-----|-----------|------------------|------|
| **Claude Code** | Claude Free: 5시간당 약 15–40 메시지 | **Pro $20/월**: 5시간당 약 10–40 프롬프트 + 주간 한도 (2025-08 도입) | claude.ai 채팅과 Claude Code가 한도를 공유 |
| **Cursor** | Hobby: 월 50 slow premium 요청 + 2,000 tab completion | **Pro $20/월**: Auto 모드 무제한 + $20 premium 크레딧 풀 + tab completion 무제한 | Fast queue는 유료에서만 |
| **Gemini CLI** | 개인 Google 계정: Flash 약 1,000 req/일, 60 RPM; Gemini 2.5 Pro는 100/일로 제한 | **Gemini Code Assist Standard $19/월**: 더 높은 할당(모델/조직별 커스터마이즈) | Pro 모델 할당이 실질적 병목 |
| **Kiro** | 월 50 크레딧 + 최초 30일 보너스 500 크레딧 | **Pro $20/월**: 월 1,000 크레딧; 초과 시 크레딧당 $0.04 (opt-in) | 2025년부터 신규 사용자 대기열 존재. 미사용 크레딧은 이월 불가 |
| **Codex CLI** | 실질적 무료 티어 없음 — ChatGPT Free는 Codex 접근 제한적 | **ChatGPT Plus $20/월**: 5시간당 GPT-5.4 로컬 메시지 약 400–2,000 + 클라우드 태스크 | Pro $100 티어 2× 프로모션 2026-05-31까지 |

*수치는 근사치입니다. 벤더가 자주 바꾸므로, 중요한 판단 전에 재확인하세요. 출처는 이 섹션 하단에 있습니다.*

### 허브가 제한 사이를 빠져나가게 하는 방법

- **Claude 5시간 한도에 걸렸다?** 같은 프로젝트를 Gemini CLI로 열기. `GEMINI.md`에 컨텍스트·에이전트·메모리가 이미 담겨 있으므로 재설명이 필요 없습니다.
- **Cursor premium 크레딧이 주중에 바닥났다?** Claude Code 또는 Codex CLI로 전환. `researcher` / `codegen` / `reviewer` 에이전트는 `.unicli-rules/agents/`에 한 번 정의되어 5개 CLI에 그대로 노출됩니다.
- **Gemini 2.5 Pro의 100/일을 어려운 문제에 아껴두고 싶다?** 루틴한 수정은 Flash(1,000/일)나 Claude Code의 같은 `codegen` 에이전트로 처리 — `conventions.md`를 공유하므로 출력 스타일도 동일.
- **Kiro 크레딧이 떨어져간다?** 여유 있는 CLI로 페일오버. 메모리와 컨벤션이 `.unicli-rules/memory/`에 있으니 다음 도구도 백지 상태가 아닌 동일 가정으로 시작합니다.
- **주머니에 구독 하나뿐?** Gemini / Kiro / Claude의 무료 티어는 각기 다른 시간대/용도를 커버합니다. 허브는 이 **합산 예산**을 사일로가 아닌 하나로 쓸 수 있게 합니다.

목표는 5개를 동시에 돌리는 게 아닙니다. **전환 비용이 0에 수렴**하기 때문에, 지금 한도가 남아 있는 CLI를 그때그때 선택해서 쓰되 프로젝트를 다시 업로드하거나 아키텍처를 다시 설명하지 않아도 된다는 점이 핵심입니다.

### 출처

- [Claude Code: rate limits, pricing, and alternatives — Northflank](https://northflank.com/blog/claude-rate-limits-claude-code-pricing-cost)
- [Using Claude Code with your Pro or Max plan — Anthropic Help Center](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Claude Code limits: quotas & rate limits guide — TrueFoundry](https://www.truefoundry.com/blog/claude-code-limits-explained)
- [Gemini CLI: quotas and pricing](https://geminicli.com/docs/resources/quota-and-pricing/)
- [Gemini 2.5 Pro free-tier daily quota (100 RPD)](https://www.aifreeapi.com/en/posts/gemini-2-5-pro-free-tier-daily-quota-rpd)
- [Gemini Code Assist quotas and limits — Google for Developers](https://developers.google.com/gemini-code-assist/resources/quotas)
- [Cursor pricing explained 2026 — Vantage](https://www.vantage.sh/blog/cursor-pricing-explained)
- [Cursor free-tier guide (50 premium + 2,000 completions)](https://eastondev.com/blog/en/posts/dev/20260110-cursor-free-quota-guide/)
- [Kiro pricing (official)](https://kiro.dev/pricing/)
- [Kiro Pro 1,000 credits details — MorphLLM](https://www.morphllm.com/kiro-pricing)
- [Codex pricing (official)](https://developers.openai.com/codex/pricing)
- [Using Codex with your ChatGPT plan — OpenAI Help Center](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)

## FAQ

**Q. Windows에서 symlink가 깨져요.**
Git for Windows의 `core.symlinks=true` 설정을 활성화하거나, `sync.sh`의 symlink 구간을 copy로 포크하세요.

**Q. Codex에서 `/unicli-researcher`가 안 보여요.**
`./.unicli-rules/sync.sh --install-codex-prompts`를 먼저 실행하세요. Codex는 프로젝트 경로가 아닌 `~/.codex/prompts/`만 스캔합니다.

**Q. 특정 CLI만 써요.**
해당 CLI의 파생 디렉토리만 사용하면 됩니다. 나머지는 무시하거나 삭제해도 됩니다. `sync.sh`에서 불필요한 단계를 지울 수도 있어요.

**Q. 에이전트 모델을 바꾸려면?**
`.unicli-rules/sync.sh`의 `CLAUDE_MODEL`, `GEMINI_MODEL` 연관 배열을 편집하세요.
