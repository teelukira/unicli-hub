# UniCLI-Hub Project Context

## Purpose

This repository is a generic fanout framework for AI CLI configuration.

It keeps canonical definitions for agents, skills, hooks, MCP servers, memory, and entry-document templates, then renders those definitions into the file layouts expected by multiple AI tools.

This repository is intentionally not tied to a delivery project, customer domain, product roadmap, or software lifecycle methodology.

## Design Boundary

Keep:

- fanout structure for agents, skills, hooks, MCP, memory, and entry docs
- renderer scripts under `.unicli-hub/scripts/`
- generated-file protection hooks
- generic examples that demonstrate framework mechanics

Do not add:

- customer or product names
- project-specific work units, roadmaps, or status snapshots
- delivery workflow gates tied to a specific tracker, repository host, or project policy
- domain-specific agents or skills
- methodology-specific lifecycle content

## Canonical Sources

| Area | Source |
|---|---|
| Agents | `hub/agents/` |
| Skills | `hub/skills/` |
| Hooks | `hub/hooks/`, `hub/claude-hooks.json`, `hub/cursor-hooks.json` |
| MCP | `hub/mcp-servers.json` |
| Memory | `hub/memory/*.md` |
| Entry templates | `.unicli-hub/templates/*.tmpl` |
| Renderers | `.unicli-hub/scripts/*.py` |

## Generated Targets

Generated targets include `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.agents/`, `.kiro/`, `.codex/`, `.grok/`, `.mcp.json`, and CLI-specific MCP/config files.

Do not edit generated targets directly. Change canonical sources and run `python sync.py --fix`.

## Current Baseline

The current baseline has no project-specific subagents and one generic skill:

- `hub/skills/html-report/`

If future work needs example agents or skills, keep them obviously generic and avoid embedding real project names, paths, credentials, tickets, or domain data.

## Verification

After changes:

```bash
python sync.py --fix
python sync.py --check
```

Then search for leaked project context before finishing:

```bash
rg -n "<known-project-name>|<known-ticket-prefix>|<known-domain-term>" hub README.md README.ko.md AGENTS.md CLAUDE.md
```
