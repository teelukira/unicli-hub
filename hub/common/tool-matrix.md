# Tool Matrix

How each AI CLI's features map to this template.

> **MCP config**: Define servers in `hub/mcp-servers.json`. `./sync.sh --fix` renders each CLI path below. Do not edit derived MCP files by hand.
> **Fan-out registry**: Target paths and orphan policy are declared in `hub/registry/fanout.json`.
> **Hook event registry**: Logical hook events and per-CLI event names are declared in `hub/registry/hook-events.json`.

| Feature | Antigravity CLI | Claude Code | Cursor | Kiro | Codex | Grok Build |
|---------|-----------------|-------------|--------|------|-------|------------|
| Agent definitions | `define_subagent` tool | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.kiro/agents/*.json` | `.codex/agents/*.toml` | `.grok/agents/*.md` |
| Entry document | `AGENTS.md` (`.agents/AGENTS.md`) | `CLAUDE.md` | `AGENTS.md` / `.cursor/rules/*.mdc` | `.kiro/steering/*.md` | `AGENTS.md` | `AGENTS.md` / `.grok/rules/*.md` |
| Skill / prompt | `.agents/skills/` | `.claude/skills/` | `.cursor/skills/` | `.kiro/skills/` | `.agents/skills/` | `.grok/skills/` |
| Hook config | `.agents/settings.json` (`BeforeTool` / `AfterTool`) | `.claude/settings.json` (`PreToolUse` / `PostToolUse`) | `.cursor/hooks.json` (`preToolUse` / `postToolUse` / shell / MCP events) | Not rendered | Not rendered | `.grok/hooks/unicli-hub.json` (`PreToolUse` / `PostToolUse` / `SessionStart` / `Stop`) |
| Hook implementation | `hub/hooks/*.py` via generated command entries | `hub/hooks/*.py` via generated command entries | `hub/hooks/*.py` via generated command entries | N/A | N/A | `hub/hooks/*.py` via generated command entries |
| Memory | `.agents/AGENTS.md` (Rules) | `CLAUDE.md` | `.cursor/rules/memory.mdc` | `.kiro/steering/03-memory.md` | `AGENTS.md` prepend | `AGENTS.md` and `.grok/rules/02-memory.md` |
| MCP | `.agents/mcp_config.json` | `.mcp.json` | `.cursor/mcp.json` | `.kiro/settings/mcp.json` | `.codex/config.toml` (`mcp_servers`) | `.grok/config.toml` (`mcp_servers`) |

## Regeneration owner

`./sync.sh` is the single orchestrator for regenerating every derived file. No CLI should overwrite another CLI's directory on its own.

`./sync.sh --check` must fail when a declared generated target drifts or when a stale generated file remains under a declared fan-out target.
