# Memory

`.unicli-rules/memory/` is the **canonical seed** for durable project facts. Its contents are propagated by `sync.sh` to each CLI's memory or context location.

## How each CLI consumes memory

| CLI | Mechanism |
|-----|-----------|
| Claude Code | Imported into `CLAUDE.md` via `@./.unicli-rules/memory/*.md` |
| Gemini CLI | Appended as a memory block at the end of `GEMINI.md` |
| Cursor | Exposed as `.cursor/rules/memory.mdc` with `alwaysApply: true` |
| Kiro | Accessible via the `.kiro/unicli-rules` symlink and copied to `.kiro/steering/03-memory.md` |
| Codex | Prepended to root `AGENTS.md` (Codex reads up to `project_doc_max_bytes`, so important facts are placed first) |

## How to edit

1. Edit the files in this directory directly.
2. Run `./.unicli-rules/sync.sh --fix`.
3. Restart the CLI (or open a new session) to pick up the new context.

## Files

- `project-facts.md` — durable project facts (team, repo, load-bearing decisions)
- `conventions.md` — coding conventions, naming, directory layout
- `glossary.md` — domain terminology
