# Consumer upgrade

How a consuming repository (not this repo) stays current with unicli-hub
without losing its own overlay.

This framework repo may `git pull` itself. A consumer must not. Consumer
`origin` is the product repo; pulling it does not update unicli-hub, and
pointing auto-update at this GitHub remote would overwrite product files.

## File classes

| Class | Paths | Update rule |
| --- | --- | --- |
| Framework | `.unicli-hub/scripts/`, `sync.sh`, `hub/common/`, `hub/templates/`, `hub/claude-hooks.json`, `hub/cursor-hooks.json`, `hub/hooks/*.py`, `scripts/mcp/run-with-env.sh`, `scripts/mcp/project-env.sh` | Replace from upstream SHA |
| Additive skills/agents | `hub/skills/<name>/`, `hub/agents/<name>.md` | Copy only if the consumer does not already have that name |
| Registry | `hub/registry/*.json` | Merge. Take new CLI targets from upstream; keep consumer command strings and extra targets |
| Overlay (never clobber) | `hub/project-context.md`, `hub/memory/`, `hub/mcp-servers.json`, `hub/kiro-steering/`, consumer-owned `hub/skills/`, `hub/agents/`, `.unicli-hub/templates/*.tmpl` if customized | Consumer owns these |
| Generated | `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.agents/`, `.kiro/`, `.codex/`, `.grok/`, `.mcp.json` | Rebuild with `./sync.sh --fix` after the copy |

`hub/hooks/generated_file_guard.py` path normalization must use the
consumer repo root, not a hard-coded `/unicli-hub/` path marker.

Hook command lines that walk a git superproject (submodule-safe) are
overlay. Upstream uses `git rev-parse --show-toplevel` only.

## Recommended loop

Pin an upstream SHA in the consumer (example: `.unicli-hub/VERSION`).

```text
1. Fetch teelukira/unicli-hub@SHA (clone --depth 1 or archive).
2. Run scripts/install-framework.sh --target <consumer> --sha <SHA>
   from this repo, or copy the same file classes by hand.
3. Review the printed registry diff. Merge fanout.json / hook-events.json
   / agent-profiles.json; do not wholesale-replace them.
4. In the consumer: ./sync.sh --fix && ./sync.sh --check
5. Commit framework + regenerated files together.
```

Do not enable session auto-pull (`hub/hooks/auto_update.py`) in a consumer
unless `origin` is this repository. The hook is fail-open and only
fast-forwards a clean tree, but the remote is the product remote.

## Why not submodule / subtree for the whole hub/

`hub/` in a consumer mixes framework files with product overlay
(project-context, memory, MCP, domain skills). A submodule cannot split
those. Vendoring framework paths and merging registries is the workable
boundary.

A submodule of **only** `.unicli-hub/` (renderers) is viable if the
consumer is willing to keep `sync.sh` and hook scripts in sync by the
installer anyway. Most of the drift is in renderers + hook scripts, not
in overlay markdown.

## Additive skills from this repo

New generic skills land under `hub/skills/` here. `install-framework.sh`
copies a skill directory only when the consumer does not already have
that directory name, so product forks of the same skill are left alone.
