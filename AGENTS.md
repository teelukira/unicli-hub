# AGENTS.md

> Shared root agent-guide document — read by Codex, Cursor, and Claude via common conventions.
> **This file is generated. Edit the canonical sources under `.unicli-rules/`.**

---

## Memory (placed at top to stay inside Codex `project_doc_max_bytes`)

# Project Facts

> **Template.** Fill in the real project facts. Leaving vague "TBD" values actively hurts AI output — be specific or delete the section.

## Team / Owner

- _TBD — responsible team or individual, Slack channel, issue tracker._

## Repository

- Primary repo: _TBD_
- Branching model: _TBD (trunk-based, gitflow, ...)_
- Default branch: `main`

## Core Decisions

- _TBD — irreversible technical choices and the reason behind them (one line each)._
- _Example: "Chose DynamoDB over PostgreSQL because of latency SLA."_

## Environments

- _TBD — dev / staging / prod endpoints and how each is deployed._

## Stakeholders

- _TBD — owners of external interfaces, reviewers._

# Conventions

Project-wide code and documentation conventions live here. AI CLIs generating or editing code must honor them.

## Naming

- File names: _TBD (kebab-case / snake_case / ...)_
- Functions: _TBD (camelCase / snake_case)_
- Constants: _TBD (UPPER_SNAKE_CASE)_
- Tests: `<module>.test.*` or `test_<module>.*`

## Directory Layout

- Source: `src/`
- Tests: `tests/` or co-located with source
- Docs: `docs/`

## Commit Messages

- Style: _TBD (e.g., Conventional Commits)_
- Issue references: _TBD_

## Code Style

- Linter: _TBD (eslint, ruff, golangci-lint, ...)_
- Formatter: _TBD (prettier, black, gofmt, ...)_
- Max line length: _TBD_
- Comments: **default to none**. Add a single line only when the *why* is non-obvious.

## Test Policy

- _TBD — coverage targets, mandatory case categories._
- Mock policy: _TBD_

## Security

- Secrets: `.env` or secret manager — never commit.
- User input is validated at boundaries; trust internal code.

# Glossary

Keep project-specific terminology here. Any word that is used with a meaning different from plain English must be recorded.

| Term | Definition | Note |
|------|------------|------|
| _TBD_ | _TBD_ | _TBD_ |

## Abbreviations

| Abbreviation | Full | Context |
|--------------|------|---------|
| _TBD_ | _TBD_ | _TBD_ |



---

## Project Context

# Project Context

> **This file is a template.** Fill in each section for your project.
> After editing, run `./.unicli-rules/sync.sh --fix` to propagate changes to every CLI.

## Project Name

_TBD — the name of this project._

## Mission

_TBD — 1–2 short paragraphs on the problem this project solves and the intended outcome._

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | _TBD_ |
| Framework | _TBD_ |
| Datastore | _TBD_ |
| Infrastructure | _TBD_ |
| Tests | _TBD_ |

## Directory Layout

```
project-root/
├── .unicli-rules/     # canonical source shared by every AI CLI (editable)
├── .claude/ .cursor/ .gemini/ .kiro/ .codex/   # derived (auto-generated)
├── src/               # application code
├── tests/
└── docs/
```

## External Integrations

_TBD — external services and APIs this project depends on._

## Constraints

_TBD — performance, security, compliance, or regulatory constraints._

## Glossary

See `.unicli-rules/memory/glossary.md`.

## Related Documents

_TBD — links to design docs, wikis, dashboards._

---

## Core Workflow

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
- `.claude/agents/*.md`
- `.cursor/rules/*.mdc`, `.cursor/agents/*.md`
- `.gemini/GEMINI.md`, `.gemini/agents/*.md`, `.gemini/skills/*/SKILL.md`
- `.kiro/steering/*.md`, `.kiro/agents/prompts/*`
- `.codex/prompts/*.md`
- MCP: `.mcp.json`, `.cursor/mcp.json`, `.kiro/mcp.json`, `.gemini/settings.json` (`mcpServers`), `.codex/config.toml` (MCP block)

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

---

## Agents & Skills

- Agent definitions: `.unicli-rules/agents/`
- Skill definitions: `.unicli-rules/skills/`
- Per-CLI derived paths: see `.unicli-rules/common/tool-matrix.md`.

## Sync

```bash
./.unicli-rules/sync.sh --fix     # regenerate all derived files
./.unicli-rules/sync.sh --check   # CI drift detection
```