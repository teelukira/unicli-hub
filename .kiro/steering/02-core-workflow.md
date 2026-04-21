# Core Workflow

This file defines the **tool-agnostic core workflow**. All five CLIs (Claude Code, Cursor, Gemini CLI, Kiro, Codex) are expected to follow these rules.

## The Three Phases

1. **Explore** — Read code, docs, and external references. Do not speculate; find evidence.
2. **Plan** — Summarize the scope and approach. Ask the user about anything uncertain.
3. **Execute** — Implement with the smallest change that works. Break work into verifiable steps.

## Approval Gates

The following actions require **explicit user approval** before running:

- Deleting files or performing large-scale refactors
- Sending anything to external systems (`git push`, opening PRs, Slack / email / Jira updates)
- Adding, removing, or upgrading dependencies or lockfiles
- Modifying production or shared resources
- Operations that incur cost (bulk calls to paid APIs, etc.)

## Generated File Rules

**Never edit derived files directly**:

- `CLAUDE.md`, `AGENTS.md` at the repository root
- `.mcp.json` at the repository root
- `.claude/agents/*.md`
- `.cursor/rules/*.mdc`, `.cursor/agents/*.md`, `.cursor/mcp.json`
- `.gemini/GEMINI.md`, `.gemini/agents/*.md`, `.gemini/skills/*/SKILL.md` (MCP section in `.gemini/settings.json`)
- `.kiro/steering/*.md`, `.kiro/agents/prompts/*`, `.kiro/settings/mcp.json`
- `.codex/prompts/*.md` (MCP sections in `.codex/config.toml`)

**Edit here instead**: `.unicli-rules/` (the canonical source).
After editing, run `./.unicli-rules/sync.sh --fix` to regenerate every derived file.

## Agent Invocation Rules

The agents defined under `.unicli-rules/agents/*.md` are available. Each CLI invokes them through its own framework (Claude sub-agents, Gemini agents, Cursor agents, Kiro agents, Codex slash commands).

- **researcher** — investigation and exploration
- **codegen** — implementation
- **reviewer** — review and critique

## Memory Usage

Treat `.unicli-rules/memory/` as a trusted starting point, but when memory conflicts with the current code, trust the code. If memory looks stale, ask the user to confirm before acting on it.

## Hand-off Conventions

When one agent hands off to another, include:

- a summary of what was done
- verified assumptions and remaining assumptions
- the list of files created or modified
- a recommendation for the next step

## Verification

Before declaring work done, confirm:

- The build and tests succeed.
- Lint and type checks pass.
- For UI changes, you exercised the feature in a browser or real usage path.
- Documentation is updated where required.
