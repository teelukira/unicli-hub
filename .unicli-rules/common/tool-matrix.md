# Tool Matrix

How each AI CLI's features map to this template.

> **MCP config**: Define servers in `.unicli-rules/common/mcp-servers.json`. `./.unicli-rules/sync.sh --fix` renders each CLI path below — do not edit derived MCP files by hand. Renderer: `.unicli-rules/hooks/render_mcp.py`.

| Feature | Claude Code | Cursor | Gemini CLI | Kiro | Codex |
|---------|-------------|--------|------------|------|-------|
| Agent definitions | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.gemini/agents/*.md` | `.kiro/agents/*.json` + prompt symlink | `.codex/prompts/*.md` (slash command) |
| Entry document | `CLAUDE.md` | `AGENTS.md` / slim `.cursor/rules/workflow.mdc` + `project-context` / `memory` | `GEMINI.md` (repo root) | `.kiro/steering/*.md` | `AGENTS.md` |
| Skill / prompt | MCP skills | `.cursor/skills/` (incl. `aidlc-*` + agent mirrors) | `.gemini/skills/<name>/SKILL.md` | `.kiro/prompts/*.md` | `~/.codex/prompts/` |
| Hook | `settings.local.json` (PreToolUse / PostToolUse) | `.cursor/hooks.json` + symlinks under `.cursor/hooks/` → `.unicli-rules/hooks/` (`*.py`, `ralph*.sh`, `java-lint-on-commit.sh`; last is Cursor-only per `sync.sh` [12aa]) | `.gemini/settings.json` | `.kiro/hooks/*.kiro.hook` | (none) |
| Memory | `CLAUDE.md` + `@import` | `.cursor/rules/memory.mdc` | `GEMINI.md` block | `.kiro/steering/03-memory.md` | `AGENTS.md` prepend |
| MCP | `.mcp.json` | `.cursor/mcp.json` | `.gemini/settings.json` | `.kiro/settings/mcp.json` | `.codex/config.toml` (`mcp_servers`) |

## Regeneration owner

`./.unicli-rules/sync.sh` is the single orchestrator for regenerating every derived file. No CLI should overwrite another CLI's directory on its own.
