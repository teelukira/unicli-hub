# Validation Spec — hub-upstream-sync

## Preconditions (machine-checkable)

- [ ] Network access available (git clone will succeed)
- [ ] `/tmp/` writable (clone target)
- [ ] `hub/.upstream-sync-state.json` readable, or absent (first run)
- [ ] `./sync.sh` executable at repo root

## Artefact contract

| Artefact | Required | Validation |
|---|---|---|
| `hub/.upstream-sync-state.json` | yes (after first run) | Must contain `last_sha`, `last_synced_at`, `divergence_acknowledged` array |
| `hub/<phase>/<file>.md` (accepted files) | conditional | Content matches upstream file at synced SHA |

## Gate marker contract

This skill has **no APPROVAL-STAGE marker** — it is a cross-cutting utility, not a workflow stage.

Per-file gates use inline 3-option choice (accept/skip/skip-forever). No audit.md writes required.

Optional: log sync summary to `aidlc-docs/audit.md` if audit logging is desired:
```
## hub-upstream-sync
**Timestamp**: <ISO-8601>
**SHA**: <upstream HEAD SHA>
**Applied**: N files — <list>
**Acknowledged divergence**: K files — <list>
---
```

## Subagent dispatch contract

- No subagents dispatched. All work done inline by this skill.

## Failure modes

| Failure | Behaviour |
|---|---|
| `git clone` fails (network/auth) | Halt with error. Do not modify local files or sync state. |
| `last_sha` not found in upstream history (force-push/rebase on upstream) | Treat as first run — diff all files in scope. Warn user. |
| Local file missing for accepted upstream file | Create new file at `hub/<phase>/<filename>`. |
| `./sync.sh --fix` fails | Report error. Local `hub/` files already updated — user must fix sync.sh manually. |
| User accepts a file that contains upstream-specific paths (e.g. `.aidlc-unicli-rules/`) | Warn after write: "Accepted file may contain upstream-specific paths. Review before committing." |
