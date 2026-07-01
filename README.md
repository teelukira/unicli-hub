# UniCLI-Hub

UniCLI-Hub is a mock/reference framework for keeping AI CLI configuration in one canonical place and fanning it out to multiple tools.

It is not an application project and should not contain customer, product, or delivery-workstream context. Its purpose is to demonstrate and maintain the mechanics for shared agents, skills, hooks, MCP servers, memory, and generated entry documents across AI CLIs.

For Korean documentation, see [README.ko.md](./README.ko.md).

## What This Framework Does

UniCLI-Hub treats `hub/` as the single source of truth and renders generated files into tool-specific locations:

| Asset | Canonical source | Generated targets |
|---|---|---|
| Entry docs | `.unicli-hub/templates/*.tmpl`, `hub/memory/`, `hub/project-context.md` | `AGENTS.md`, `CLAUDE.md` |
| Agents | `hub/agents/` | `.claude/agents/`, `.cursor/agents/`, `.agents/`, `.kiro/`, `.codex/prompts/` |
| Skills | `hub/skills/` | `.claude/skills/`, `.cursor/skills/`, `.agents/skills/`, `.kiro/steering/skill-*.md`, `.codex/prompts/skill-*.md` |
| Hooks | `hub/hooks/`, `hub/registry/hook-events.json` | `.claude/settings.json`, `.cursor/hooks.json`, `.agents/settings.json` |
| MCP servers | `hub/mcp-servers.json` | `.mcp.json`, `.cursor/mcp.json`, `.agents/mcp_config.json`, `.codex/config.toml` |
| Memory | `hub/memory/*.md` | embedded in generated entry docs |

## Supported CLIs

| CLI | Derived location | Entry point |
|---|---|---|
| Antigravity / agy | `.agents/` | `AGENTS.md` |
| Claude Code | `.claude/` | `CLAUDE.md` |
| Cursor | `.cursor/` | `AGENTS.md` plus Cursor files |
| Kiro | `.kiro/` | generated steering and agent files |
| OpenAI Codex | `.codex/` | `AGENTS.md` plus prompt files |

## Tool Capabilities (Skills, Subagents, MCP)

Different AI CLIs handle extended capabilities in their own distinct ways. This framework abstracts these differences, but it is helpful to understand how each tool implements them:

### 1. Google Antigravity (agy)
- **Skills**: Fully supported natively. Skills are loaded directly from the workspace customization root (`.agents/skills/<skill_name>/SKILL.md`).
- **Subagents**: Supported dynamically. Instead of defining custom subagents via static files, Antigravity uses robust built-in subagents (e.g., `research`, `self`) and allows agents to spawn subagents dynamically via the `define_subagent` tool during runtime.
- **MCP**: Supported via directory structure. Antigravity expects MCP tool schemas in specific folders (e.g., `mcp/<serverName>/<toolName>.json`) rather than a single unified configuration file.

### 2. Cursor
- **Skills**: Supported via IDE rules. Skills are implemented as `.cursor/rules/*.mdc` files.
- **Subagents**: Supported statically. Cursor loads markdown definitions from `.cursor/agents/*.md` to configure IDE subagents.
- **MCP**: Fully supported via a unified config file (`.cursor/mcp.json`) for straightforward server connections.

### 3. Claude Code
- **Skills**: Fully supported natively via `.claude/skills/`.
- **Subagents**: Supported statically. Defines custom agent roles and system prompts through markdown files in `.claude/agents/*.md`.
- **MCP**: Fully supported via the project-root `.mcp.json` unified configuration file.

## Repository Layout

```text
.
├── hub/                    # canonical framework content
│   ├── registry/           # fanout, hook-event, and model-profile registries
│   ├── agents/             # optional source agent prompts
│   ├── skills/             # optional source skills
│   ├── hooks/              # hook scripts shared across CLIs
│   ├── memory/             # generated entry-doc memory snippets
│   ├── common/             # framework reference docs
│   ├── mcp-servers.json    # MCP server registry
│   └── project-context.md  # framework context for future agents
├── .unicli-hub/            # renderer implementation and templates
│   ├── scripts/            # render_agents/render_skills/render_hooks/render_mcp/render_templates
│   └── templates/          # AGENTS.md and CLAUDE.md templates
├── sync.sh                 # one command to regenerate all targets
├── AGENTS.md               # generated
└── CLAUDE.md               # generated
```

## Working Rules

Edit canonical files under `hub/` or `.unicli-hub/templates/`.

Do not edit generated targets directly: `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.agents/`, `.kiro/`, `.codex/`, `.mcp.json`, and generated MCP/config files. The generated-file hook points edits back to the canonical source.

After changing canonical content, run:

```bash
./sync.sh --fix
./sync.sh --check
```

`--fix` regenerates derived files and removes stale generated agents/skills. `--check` fails if any generated output has drifted.

## Current Baseline

This framework is intentionally generic. The current baseline keeps:

- registry-driven fanout renderers for agents, skills, hooks, static copies, MCP, and entry templates
- generated-file protection hooks
- MCP propagation structure
- one generic example skill: `html-report`
- memory placeholders for project facts, conventions, and glossary

This baseline intentionally excludes:

- methodology-specific lifecycle workflow content
- customer or product-specific agents and skills
- delivery gate policy tied to a specific issue tracker or forge
- domain-specific context

## Adding Content

To add an agent, place source files in `hub/agents/`; add optional model profiles in `hub/registry/agent-profiles.json`; then run `./sync.sh --fix`.

To add a skill, create `hub/skills/<skill-name>/SKILL.md`; optional support files can live beside it. The skill renderer copies folder contents and reference files to supported targets.

To add or remove MCP servers, edit `hub/mcp-servers.json`. Keep secrets out of the file; use inherited environment variables or wrapper scripts where a CLI cannot expand environment variables in JSON args.

To change generated entry document wording, edit `.unicli-hub/templates/AGENTS.md.tmpl` or `.unicli-hub/templates/CLAUDE.md.tmpl`.

## Registry Files

- `hub/registry/hook-events.json`: maps logical hook events to each CLI's event names.
- `hub/registry/fanout.json`: declares source/target paths and orphan policy for agents, skills, and static copies.
- `hub/registry/agent-profiles.json`: stores generated Codex prompt model metadata for subagents.
