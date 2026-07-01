# hub/ - unicli-hub SSOT

This directory is the Single Source of Truth for the unicli-hub framework.
`./sync.sh --fix` regenerates all derived files from here.

## Architecture Overview

```text
hub/
  ├─ registry/            # machine-readable fanout, hook-event, model profile SSOT
  ├─ agents/              # canonical subagent definitions
  ├─ skills/              # canonical skill definitions
  ├─ hooks/               # canonical hook scripts and guard skeletons
  ├─ memory/              # optional generated entry-document memory
  ├─ mcp-servers.json     # canonical MCP server registry
  └─ common/              # framework reference docs
```

## Registry SSOT

`hub/registry/` is the machine-readable source for generated AI CLI assets.

| Registry | Purpose | Renderer |
|----------|---------|----------|
| `hook-events.json` | Logical hook events and per-CLI event names (`PreToolUse`, `preToolUse`, `BeforeTool`, etc.) | `.unicli-hub/scripts/render_hooks.py` |
| `fanout.json` | Skill, subagent, static-copy, and MCP target paths plus orphan policy | `render_agents.py`, `render_skills.py`, `render_static.py`, `render_mcp.py` |
| `agent-profiles.json` | Per-agent model/reasoning profiles for generated Codex and Cursor subagents | `render_agents.py` |

Rules that can be checked mechanically should live in hook or verification scripts, with Markdown retaining only the contract and source paths.

## Adding an Agent

1. Add `hub/agents/<agent-name>.md`.
2. Optional CLI profiles in `hub/registry/agent-profiles.json`:
   - `cursor.<agent-name>` for `model`, `readonly`, `is_background`
   - `codex.<agent-name>` for generated Codex prompt model metadata
3. Run `./sync.sh --fix`.

## Adding a Skill

1. Create `hub/skills/<name>/`.
2. Write `SKILL.md` with frontmatter:

   ```yaml
   ---
   name: <name>
   description: >-
     [What the skill does] + [When to use it with trigger phrases].
   allowed-tools: [Read, Edit, Write]
   ---
   ```

3. Add optional support files beside `SKILL.md`; the renderer copies them to supported skill targets.
4. Run `./sync.sh --fix`.

## Verification Checklist

| Test | What to verify | Pass condition |
|------|---------------|----------------|
| F.1 Fanout | Agents, skills, hooks, MCP render to derived targets | Expected files are generated |
| F.2 Reconcile | Removed canonical agents/skills/static files are removed from derived targets | No stale generated files remain |
| F.3 Idempotence | `./sync.sh --fix` then `./sync.sh --check` | `--check` exits 0 |
| F.4 Hook event map | Hook event names differ by CLI but render from `hub/registry/hook-events.json` | Generated hook configs use the expected target event names |
