# UniCLI-Hub: The Frugal AI Nomad's Workspace

> *(Company won't sponsor your tools? We got you.)*

**UniCLI-Hub** is a centralized context management workspace for developers who are tired of AI subscription fatigue.

## Why did I build this? (The "Broke Developer" Problem)

Let's be honest. AI tools are amazing, but paying $20/month for *every single one* of them is not. Maybe your company doesn't sponsor AI tools, or maybe you just want to maximize the free tiers of Gemini, Claude Code, Cursor, and Kiro-CLI without losing your mind.

When you constantly hop between Free/Basic tiers of different AI CLIs to bypass token limits, your AI's "brain" becomes fragmented. Your `agent.md` is here, your custom skills are there, and the AI keeps forgetting the project context.

## The Solution

**UniCLI-Hub** acts as the Single Source of Truth (SSOT) for your AI workflows. It centralizes your sub-agents, memory, and skills so you can seamlessly switch to another tool the moment you hit a rate limit.

**With UniCLI-Hub, you can:**

- **Run out of Claude tokens?** Switch to Gemini CLI without re-explaining your entire project architecture.
- **Keep a unified memory:** Share `.cursorrules`, Kiro system prompts, and Claude contexts from one single directory.
- **Save Money:** Maximize your productivity using a combination of free tiers and single subscriptions without losing the "Pro" experience.

> Prefer 한국어? See [README.ko.md](./README.ko.md).

---

## Supported CLIs

| CLI | Derived location | Entry point |
|-----|------------------|-------------|
| Claude Code | `.claude/` | `CLAUDE.md` |
| Cursor | `.cursor/rules/`, `.cursor/agents/` | `.cursor/rules/*.mdc` |
| Gemini CLI | `.gemini/` | `.gemini/GEMINI.md` |
| Kiro | `.kiro/steering/`, `.kiro/agents/` | `.kiro/steering/*.md` |
| OpenAI Codex | `.codex/`, `AGENTS.md` | `AGENTS.md` (root) |

## Quick Start

```bash
# 1) Clone (or use this directory as a starting point)
git clone <this-repo> my-project && cd my-project

# 2) Edit the canonical sources to match your project
#    - .unicli-rules/project-context.md
#    - .unicli-rules/memory/project-facts.md
#    - .unicli-rules/memory/conventions.md
#    - .unicli-rules/memory/glossary.md

# 3) Regenerate every CLI's derived files
./.unicli-rules/sync.sh --fix

# 4) Open the project with any supported CLI
claude                # Claude Code
cursor .              # Cursor
gemini                # Gemini CLI
kiro                  # Kiro
codex                 # Codex (loads AGENTS.md automatically)
```

## Canonical vs Derived

**Edit these files** (`.unicli-rules/`):

```
.unicli-rules/
├── core-workflow.md          # tool-agnostic workflow
├── project-context.md        # project context
├── agents/{researcher,codegen,reviewer}.md
├── skills/{scaffold-module,run-tests}.md
├── memory/{project-facts,conventions,glossary}.md
├── common/{tool-matrix,approval-gates}.md, mcp-servers.json
├── templates/
│   ├── CLAUDE.md.tmpl
│   ├── GEMINI.md.tmpl
│   ├── AGENTS.md.tmpl
│   └── frontmatter/*.yaml
├── hooks/
│   ├── generated_file_guard.py   # PreToolUse  — blocks edits to derived files
│   ├── auto_sync.py              # PostToolUse — runs sync.sh on canonical edits
│   └── render_mcp.py             # renders MCP configs for all five CLIs
└── sync.sh
```

**Never edit these (auto-generated)**:

- `CLAUDE.md`, `AGENTS.md` at the root
- `.claude/agents/*.md`
- `.cursor/rules/*.mdc`, `.cursor/agents/*.md`, `.cursor/skills/*`
- `.gemini/GEMINI.md`, `.gemini/agents/*.md`, `.gemini/skills/*`
- `.kiro/steering/*.md`, `.kiro/agents/prompts/*` (symlink)
- `.codex/prompts/*.md`
- MCP (from `common/mcp-servers.json`): `.mcp.json`, `.cursor/mcp.json`, `.kiro/mcp.json`, `.gemini/settings.json` (`mcpServers` key), `.codex/config.toml` (generated `[[mcpServers]]` block)

If an agent tries to edit any of these directly, the `generated_file_guard.py` PreToolUse hook blocks the write and tells it to edit the canonical source instead.

## The Rule: Only `sync.sh` Touches Derived Directories

- Editing via **`./.unicli-rules/sync.sh`** is the one sanctioned path into `.cursor/`, `.claude/`, `.gemini/`, `.kiro/`, `.codex/`.
- Any other write (by an AI agent or by hand) to those directories is blocked by the Python guard hook.
- Want to change an agent's prompt, a skill, memory, or MCP servers? Edit under `.unicli-rules/`, run `sync.sh --fix`. That's the only workflow.

## Adding a New Agent

```bash
# 1) Write the canonical prompt
cat > .unicli-rules/agents/security-scanner.md <<'EOF'
# Security Scanner Agent
...
EOF

# 2) Add the name to the SHARED_AGENTS array in sync.sh
#    (and specify description, tool allowlist, model)

# 3) Regenerate
./.unicli-rules/sync.sh --fix
```

## Adding a New Skill

Just create `.unicli-rules/skills/<name>.md`. `sync.sh` fans it out to Gemini and Cursor automatically.

### Skill Secrets Management

Do not store raw API keys or secrets in your skill directories (e.g. `utils/*.json`). Instead:
1. Store secrets in the project root `.env.local` (which is git-ignored).
2. Use `python-dotenv` to dynamically load secrets by searching upwards for the `.env.local` file.
3. See the provided example in `.unicli-rules/skills/example-skill/utils/secrets_manager.py`.

## Editing Memory

1. Edit any file under `.unicli-rules/memory/`.
2. Run `./.unicli-rules/sync.sh --fix`.
3. Restart your CLI session (or start a new thread) to pick up the new context.

## Hooks (Python)

| Hook | Trigger | Behavior |
|------|---------|----------|
| `generated_file_guard.py` | PreToolUse (Edit / Write) | Blocks direct edits to derived files and prints the canonical source to edit. |
| `auto_sync.py` | PostToolUse (Edit / Write) | When a file under `.unicli-rules/**` is modified, runs `sync.sh --fix` automatically. |
| `pre_skill_sync.py` | Cursor `beforeReadFile` (Read / TabRead); Gemini `BeforeTool` (`read_file`) | Before reading a skill path, runs `sync.sh --fix` so derived `SKILL.md` files match `.unicli-rules/skills/`. |

### Skill sync on other CLIs

- **Codex** — No project hooks in this template; run `./.unicli-rules/sync.sh --fix` manually before using skills.
- **Kiro** — This repo only wires `beforeFileWrite` / `afterFileWrite` hooks; there is no read-time hook here — use manual sync before skills.
- **Claude Code** — Optional: add a read-time hook that runs `python3 ./.unicli-rules/hooks/pre_skill_sync.py` (see `.unicli-rules/templates/claude-pre-skill-sync.snippet.json` for a mergeable fragment; confirm field names against current Claude Code docs), or run `./.unicli-rules/sync.sh --fix` manually.

The hooks are pure-Python (stdlib only) and run on Python 3.8+. All five CLIs' hook configs (`.claude/settings.local.json`, `.cursor/hooks.json`, `.gemini/settings.json`, `.kiro/hooks/*.kiro.hook`) call them via `python3`.

## Installing Codex Prompts

Codex only exposes prompts from `~/.codex/prompts/` as slash commands. Install them from this project with:

```bash
./.unicli-rules/sync.sh --install-codex-prompts
# Available afterwards: /unicli-researcher, /unicli-codegen, /unicli-reviewer
```

## CI Integration

Example `.github/workflows/sync-check.yml`:

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

`sync.sh --check` exits non-zero whenever a derived file drifts from the canonical source, so any PR that forgot to run `--fix` fails CI.

## Dodging the Rate Limits (April 2026 snapshot)

Every AI CLI caps its free and $20/mo tier tightly, and those caps are **independent per vendor**. That's the whole reason UniCLI-Hub exists: share one canonical context across all five and rotate between them whenever you hit a wall.

### Free vs. $20/mo tier — side-by-side

| CLI | Free tier | $20/mo paid tier | Notes |
|-----|-----------|------------------|-------|
| **Claude Code** | Claude Free: ~15–40 messages / 5h | **Pro $20/mo**: ~10–40 prompts / 5h + weekly cap (introduced Aug 2025) | Caps are shared between claude.ai chat and Claude Code. |
| **Cursor** | Hobby: 50 slow premium requests + 2,000 tab completions / month | **Pro $20/mo**: unlimited Auto mode + $20 premium credit pool + unlimited completions | Fast queue only on paid plans. |
| **Gemini CLI** | Personal Google account: ~1,000 requests/day on Flash, 60 RPM; Gemini 2.5 Pro capped at 100/day | **Gemini Code Assist Standard $19/mo**: higher quotas (customizable per model/org) | Pro-model quota is the real scarce resource. |
| **Kiro** | 50 credits/month + 500 bonus credits (first 30 days) | **Pro $20/mo**: 1,000 credits/month; overage $0.04/credit (opt-in) | New-user waitlist active since 2025. Unused credits don't roll over. |
| **Codex CLI** | No true free tier — ChatGPT Free has only limited Codex access | **ChatGPT Plus $20/mo**: ~400–2,000 GPT-5.4 local messages / 5h, plus cloud tasks | 2× Codex-usage promo on Pro $100 tier runs through May 31, 2026. |

*Numbers approximate. Providers change these frequently; re-check before relying on them. Sources are listed at the bottom of this section.*

### How this hub lets you slip between the caps

- **Claude's 5-hour cap kicked in mid-task?** Open the same project in Gemini CLI — `GEMINI.md` already carries your context, agents, and memory. No re-briefing.
- **Used up Cursor premium credits before the week ends?** Switch to Claude Code or Codex CLI. Your `researcher` / `codegen` / `reviewer` agents are defined once in `.unicli-rules/agents/` and exposed to all five CLIs.
- **Saving Gemini 2.5 Pro's 100/day for hard problems?** Burn routine edits through Flash (1,000/day) or Claude Code via the same `codegen` agent — same output style because they share `conventions.md`.
- **Kiro credits running dry?** Fail over to whichever CLI still has budget. Since memory and conventions live in `.unicli-rules/memory/`, the next tool starts with identical assumptions, not a blank slate.
- **Only one subscription in your pocket?** Free tiers across Gemini / Kiro / Claude each cover a different slice of the day — the hub makes that *combined budget* usable instead of siloed.

The goal isn't to run all five at once. It's that **switching costs drop to zero**, so whichever CLI is under its cap *right now* is the one you use — without re-uploading your project or re-explaining your architecture.

### Sources

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

**Q. Symlinks are broken on Windows.**
Enable `core.symlinks=true` in Git for Windows, or fork `sync.sh` to replace the symlink steps with copies.

**Q. `/unicli-researcher` doesn't show up in Codex.**
Run `./.unicli-rules/sync.sh --install-codex-prompts` first — Codex scans `~/.codex/prompts/`, not the project path.

**Q. I only use one CLI.**
Use that CLI's derived directory. The others can be ignored or deleted. You can also trim the steps in `sync.sh` that you don't need.

## Recent Updates

- **Unified Secret Management**: Introduced `python-dotenv` integration for skills to safely load secrets from the root `.env.local` file.
- **Agent Model Management**: Centralized model configuration for agents in SSOT.
- **MCP Configuration**: Unified MCP server definitions across all 5 supported CLIs.

**Q. How do I change agent models?**
Edit the `CLAUDE_MODEL` / `GEMINI_MODEL` associative arrays in `.unicli-rules/sync.sh`.
