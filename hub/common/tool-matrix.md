# Tool Matrix

How each AI CLI's features map to this template.

> **MCP config**: Define servers in `hub/mcp-servers.json`. `./sync.sh --fix` renders each CLI path below. Do not edit derived MCP files by hand.
> **Fan-out registry**: Target paths and orphan policy are declared in `hub/registry/fanout.json`.
> **Hook event registry**: Logical hook events and per-CLI event names are declared in `hub/registry/hook-events.json`.

| Feature | Antigravity CLI | Claude Code | Cursor | Kiro | Codex |
|---------|-----------------|-------------|--------|------|-------|
| Agent definitions | `define_subagent` tool | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.kiro/steering/*.md` references | `.codex/prompts/*.md` |
| Entry document | `AGENTS.md` (`.agents/AGENTS.md`) | `CLAUDE.md` | `AGENTS.md` / `.cursor/rules/*.mdc` | `.kiro/steering/*.md` | `AGENTS.md` |
| Skill / prompt | `.agents/skills/` | `.claude/skills/` | `.cursor/skills/` | `.kiro/steering/skill-*.md` | `.codex/prompts/skill-*.md` |
| Hook config | `.agents/settings.json` (`BeforeTool` / `AfterTool`) | `.claude/settings.json` (`PreToolUse` / `PostToolUse`) | `.cursor/hooks.json` (`preToolUse` / `postToolUse` / shell / MCP events) | Not rendered | Not rendered |
| Hook implementation | `hub/hooks/*.py` via generated command entries | `hub/hooks/*.py` via generated command entries | `hub/hooks/*.py` via generated command entries | N/A | N/A |
| Memory | `.agents/AGENTS.md` (Rules) | `CLAUDE.md` | `.cursor/rules/memory.mdc` | `.kiro/steering/03-memory.md` | `AGENTS.md` prepend |
| MCP | `mcp/` directory structure (Global/Workspace) | `.mcp.json` | `.cursor/mcp.json` | `.kiro/settings/mcp.json` | `.codex/config.toml` (`mcp_servers`) |

## Regeneration owner

`./sync.sh` is the single orchestrator for regenerating every derived file. No CLI should overwrite another CLI's directory on its own.

`./sync.sh --check` must fail when a declared generated target drifts or when a stale generated file remains under a declared fan-out target.
