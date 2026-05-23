# Tool Matrix

How each AI CLI's features map to this template.

> **MCP config**: Define servers in `hub/common/mcp-servers.json`. `./sync.sh --fix` renders each CLI path below — do not edit derived MCP files by hand. Renderer: `hub/hooks/render_mcp.py`.

| Feature | Antigravity CLI | Claude Code | Cursor | Kiro | Codex |
|---------|-----------------|-------------|--------|------|-------|
| Agent definitions | `.agents/agents/<name>/agent.json` | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.kiro/agents/*.json` + prompt symlink | `.codex/prompts/*.md` (slash command) |
| Entry document | `ANTIGRAVITY.md` | `CLAUDE.md` | `AGENTS.md` / slim `.cursor/rules/workflow.mdc` + `project-context` / `memory` | `.kiro/steering/*.md` | `AGENTS.md` |
| Skill / prompt | `.agents/skills/` | MCP skills | `.cursor/skills/` (incl. `aidlc-*` + agent mirrors) | `.kiro/prompts/*.md` | `~/.codex/prompts/` |
| Hook | `.agents/settings.json` | `settings.local.json` (PreToolUse / PostToolUse) | `.cursor/hooks.json` + regular files copied to `.cursor/hooks/` from `hub/hooks/` (`*.py`, `ralph*.sh`, `java-lint-on-commit.sh`; last is Cursor-only per `sync.sh`) | `.kiro/hooks/*.kiro.hook` | (none) |
| Memory | `AGENTS.md` | `CLAUDE.md` + `@import` | `.cursor/rules/memory.mdc` | `.kiro/steering/03-memory.md` | `AGENTS.md` prepend |
| MCP | `.agents/mcp_config.json` | `.mcp.json` | `.cursor/mcp.json` | `.kiro/settings/mcp.json` | `.codex/config.toml` (`mcp_servers`) |

## Regeneration owner

`./sync.sh` is the single orchestrator for regenerating every derived file. No CLI should overwrite another CLI's directory on its own.
