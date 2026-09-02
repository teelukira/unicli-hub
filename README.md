# UniCLI-Hub

UniCLI-Hub is a mock/reference framework for keeping AI CLI configuration in one canonical place and fanning it out to multiple tools.

It is not an application project and should not contain customer, product, or delivery-workstream context. Its purpose is to demonstrate and maintain the mechanics for shared agents, skills, hooks, MCP servers, memory, and generated entry documents across AI CLIs.

For Korean documentation, see [README.ko.md](./README.ko.md).

## What This Framework Does

UniCLI-Hub treats `hub/` as the single source of truth and renders generated files into tool-specific locations:

| Asset | Canonical source | Generated targets |
|---|---|---|
| Entry docs | `.unicli-hub/templates/*.tmpl`, `hub/memory/`, `hub/project-context.md` | `AGENTS.md`, `CLAUDE.md` |
| Agents | `hub/agents/` | `.claude/agents/`, `.cursor/agents/`, `.agents/`, `.kiro/agents/`, `.codex/agents/`, `.grok/agents/` |
| Skills | `hub/skills/` | `.claude/skills/`, `.cursor/skills/`, `.agents/skills/`, `.kiro/skills/`, `.grok/skills/` |
| Hooks | `hub/hooks/`, `hub/registry/hook-events.json` | `.claude/settings.json`, `.cursor/hooks.json`, `.agents/settings.json`, `.grok/hooks/unicli-hub.json` |
| MCP servers | `hub/mcp-servers.json` | `.mcp.json`, `.cursor/mcp.json`, `.agents/mcp_config.json`, `.kiro/settings/mcp.json`, `.codex/config.toml`, `.grok/config.toml` |
| Memory | `hub/memory/*.md` | embedded in generated entry docs |

## Supported CLIs

| CLI | Derived location | Entry point |
|---|---|---|
| Antigravity / agy | `.agents/` | `AGENTS.md` |
| Claude Code | `.claude/` | `CLAUDE.md` |
| Cursor | `.cursor/` | `AGENTS.md` plus Cursor files |
| Kiro | `.kiro/` | generated steering and agent files |
| OpenAI Codex | `.codex/` | `AGENTS.md` plus agent and skill files |
| Grok Build | `.grok/` | `AGENTS.md` plus `.grok/` agents, skills, hooks, and MCP |

## Tool Capabilities (Skills, Subagents, MCP)

Different AI CLIs handle extended capabilities in their own distinct ways. This framework abstracts these differences, but it is helpful to understand how each tool implements them:

### 1. Google Antigravity (agy)
- **Skills**: Fully supported natively. Skills are loaded directly from the workspace customization root (`.agents/skills/<skill_name>/SKILL.md`).
- **Subagents**: Supported dynamically. Instead of defining custom subagents via static files, Antigravity uses robust built-in subagents (e.g., `research`, `self`) and allows agents to spawn subagents dynamically via the `define_subagent` tool during runtime.
- **MCP**: Workspace MCP config at `.agents/mcp_config.json` (`mcpServers`). Global config lives at `~/.gemini/config/mcp_config.json`.

### 2. Cursor
- **Skills**: Native Agent Skills at `.cursor/skills/<skill_name>/SKILL.md`. Cursor also loads `.agents/skills/` and Claude/Codex skill directories for compatibility. Always-on project rules remain `.cursor/rules/*.mdc`.
- **Subagents**: Static markdown at `.cursor/agents/*.md` with YAML frontmatter (`name`, `description`, `model`, `readonly`, `is_background`).
- **MCP**: Project `.cursor/mcp.json`.

### 3. Claude Code
- **Skills**: Native `.claude/skills/<skill_name>/SKILL.md`.
- **Subagents**: Markdown plus YAML frontmatter in `.claude/agents/*.md` (`name`, `description`, optional `tools`, `model` alias such as `sonnet`).
- **MCP**: Project-root `.mcp.json`.

### 4. Grok Build
- **Skills**: Native project skills at `.grok/skills/<skill_name>/SKILL.md`. Grok can also scan Claude, Cursor, and Antigravity skill directories via compatibility settings; native `.grok/skills/` wins on name collision.
- **Subagents**: Native markdown agent definitions at `.grok/agents/*.md` with YAML frontmatter (`name`, `description`, `model`, `permission_mode`). Spawned at runtime via `spawn_subagent`.
- **MCP**: Project-scoped TOML at `.grok/config.toml` under `[mcp_servers.<name>]`. Native Grok config takes priority over Claude, Cursor, and `.mcp.json` compatibility sources.
- **Trust**: Project `.grok/hooks/` and repo-local MCP servers run only after the folder is trusted (`/hooks-trust` or `grok --trust`).

### 5. OpenAI Codex
- **Skills**: Repo skills are `.agents/skills/<skill_name>/SKILL.md` (shared Agent Skills location with Antigravity). User skills live in `$HOME/.agents/skills`.
- **Subagents**: Project custom agents are TOML files at `.codex/agents/*.toml` with `name`, `description`, and `developer_instructions`.
- **MCP**: Project `.codex/config.toml` under `[mcp_servers.<name>]`.

### 6. Kiro
- **Skills**: Native Agent Skills at `.kiro/skills/<skill_name>/SKILL.md`. Steering files under `.kiro/steering/` remain always-on project context, not skills.
- **Subagents**: Custom agents at `.kiro/agents/*.json` (JSON remains valid; `prompt` and tag-based `tools` such as `read` / `write` / `shell`).
- **MCP**: `.kiro/settings/mcp.json`.

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

Do not edit generated targets directly: `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.agents/`, `.kiro/`, `.codex/`, `.grok/`, `.mcp.json`, and generated MCP/config files. The generated-file hook points edits back to the canonical source.

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
- generic skills: `html-report`, `confluence-page`, `email-html-report`
- memory placeholders for project facts, conventions, and glossary

This baseline intentionally excludes:

- methodology-specific lifecycle workflow content
- customer or product-specific agents and skills
- delivery gate policy tied to a specific issue tracker or forge
- domain-specific context

## Adding Content

To add an agent, place source files in `hub/agents/`; add optional model profiles in `hub/registry/agent-profiles.json`; then run `./sync.sh --fix`.

To add a skill, create `hub/skills/<skill-name>/SKILL.md`; optional support files can live beside it. The skill renderer copies folder contents and reference files to supported targets.

Consuming product repos should not `git pull` this repository as `origin`. See `hub/common/consumer-upgrade.md` and `scripts/install-framework.sh`.

To add or remove MCP servers, edit `hub/mcp-servers.json`. Keep secrets out of the file; use inherited environment variables or credential-checking wrapper scripts.

All stdio MCP servers are rendered through `scripts/mcp/run-with-env.sh`. The generated launcher resolves the active Git worktree from any directory below it, then loads environment files in this precedence order: parent process, current worktree `.env.local`, current worktree `.env`, primary worktree `.env.local`, primary worktree `.env`. This lets the primary worktree provide shared local defaults while linked worktrees override them. Set `"_project_env": false` on a server only when it must bypass this behavior.

To change generated entry document wording, edit `.unicli-hub/templates/AGENTS.md.tmpl` or `.unicli-hub/templates/CLAUDE.md.tmpl`.

## Registry Files

- `hub/registry/hook-events.json`: maps logical hook events to each CLI's event names.
- `hub/registry/fanout.json`: declares source/target paths and orphan policy for agents, skills, and static copies.
- `hub/registry/agent-profiles.json`: stores generated Codex prompt model metadata for subagents.
