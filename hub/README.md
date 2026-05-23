# hub/ — unicli-hub SSOT

This directory is the Single Source of Truth for the unicli-hub framework.
`./sync.sh --fix` regenerates all derived files from here.

## Architecture Overview

```
hub/
  ├─ agents/             # canonical subagent definitions
  ├─ skills/             # canonical skill definitions
  ├─ hooks/              # canonical hook scripts
  ├─ memory/             # optional generated entry-document memory
  ├─ mcp-servers.json    # canonical MCP server registry
  └─ common/             # framework reference docs
```

## Adding a Skill

1. **Create folder**: `hub/skills/<name>/`

2. **Write `SKILL.md`** with required frontmatter:
   ```yaml
   ---
   name: <name>
   description: >-
     [What the skill does] + [When to use it with trigger phrases].
   allowed-tools: [Read, Edit, Write]
   ---
   ```

2. **Regenerate**: `./sync.sh --fix`

---

## Verification Checklist

| Test | What to verify | Pass condition |
|------|---------------|----------------|
| F.1 Fanout | Agents, skills, hooks, MCP render to derived targets | Expected files are generated |
| F.2 Reconcile | Removed canonical agents/skills are removed from derived targets | No stale generated files remain |
| F.3 Idempotence | `./sync.sh --fix` then `./sync.sh --check` | `--check` exits 0 |
