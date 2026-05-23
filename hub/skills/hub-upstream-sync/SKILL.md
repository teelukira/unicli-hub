---
name: hub-upstream-sync
description: >-
  Sync hub/ SSOT from awslabs/aidlc-workflows upstream methodology rules. Use
  whenever you want to check for AI-DLC methodology updates, pull new rule
  content from upstream, or review what has changed since the last sync.
  Trigger phrases: "upstream sync", "check for aidlc updates", "update from
  aws aidlc", "pull upstream changes", "sync methodology rules".
allowed-tools: [Read, Edit, Write, Bash]
phase: cross-cutting
stage: hub-upstream-sync
per-unit: false
human-clarification: required
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# hub-upstream-sync

**Purpose**: Pull methodology rule updates from `awslabs/aidlc-workflows` into `hub/` with human-in-the-loop diff review. Never auto-overwrites — every file change requires explicit user approval.

## Upstream Path Mapping

| Upstream (`aidlc-rules/aws-aidlc-rule-details/`) | Local (`hub/`) |
|---|---|
| `common/*.md` | `hub/common/` |
| `inception/*.md` | `hub/inception/` |
| `construction/*.md` | `hub/construction/` |
| `extensions/security/*.md` | `hub/extensions/security/` |
| `extensions/testing/*.md` | `hub/extensions/testing/` |
| `operations/*.md` | `hub/operations/` |

**Never synced** (orion-specific, no upstream equivalent):
`hub/skills/`, `hub/hooks/`, `hub/agents/`, `hub/memory/`, `hub/templates/`,
`hub/kiro-steering/`, `hub/extensions/adr/`, `hub/extensions/tmf/`

---

## Step 0: Load sync state

Read `hub/.upstream-sync-state.json`. If absent, create with defaults (first run):
```json
{
  "last_sha": null,
  "last_synced_at": null,
  "divergence_acknowledged": []
}
```

`divergence_acknowledged` — list of upstream-relative paths (e.g. `common/terminology.md`) where local intentional divergence has been permanently accepted. These files are skipped in all future syncs.

## Step 1: Clone upstream

```bash
rm -rf /tmp/aidlc-upstream
git clone --depth 1 https://github.com/awslabs/aidlc-workflows.git /tmp/aidlc-upstream
```

Get current HEAD SHA:
```bash
git -C /tmp/aidlc-upstream rev-parse HEAD
```

If `last_sha` equals current HEAD: display "Already up to date (SHA: `<sha>`). No changes since last sync on `<last_synced_at>`." and exit.

## Step 2: Identify candidate files

**First run** (`last_sha` is null): all files under `aidlc-rules/aws-aidlc-rule-details/` matching the mapping table above are candidates.

**Subsequent runs**: get files changed in upstream since last sync:
```bash
git -C /tmp/aidlc-upstream log --name-only --pretty=format: \
  <last_sha>..HEAD -- 'aidlc-rules/aws-aidlc-rule-details/'
```

Filter candidates to only those in the mapping scope. Remove any paths in `divergence_acknowledged`.

## Step 3: Display sync summary

```
## hub-upstream-sync

Upstream:     awslabs/aidlc-workflows @ <sha> (0.1.x)
Last synced:  <last_sha> on <last_synced_at>   [or: "never (first run)"]

Files to review: N
  • common/terminology.md
  • inception/requirements-analysis.md
  ...

Skipped (divergence_acknowledged): M files
```

If N = 0: update sync state to current SHA and exit — "No methodology rule changes since last sync."

## Step 4: Per-file diff review (BLOCKING)

For each candidate file (one at a time):

1. Resolve paths:
   - `upstream_path` = `/tmp/aidlc-upstream/aidlc-rules/aws-aidlc-rule-details/<rel_path>`
   - `local_path` = `hub/<mapped_phase>/<filename>`

2. Read both files. If local file does not exist, show as **NEW FILE**.

3. Generate unified diff:
   ```bash
   diff -u <local_path> <upstream_path>
   ```
   Or show full file if local is absent.

4. Present to user:

```
### File [i/N]: hub/<local_path>

<unified diff or NEW FILE content>

---
**Option 1 — Accept**: Apply upstream content to local file.
**Option 2 — Skip (this time)**: Keep local as-is; diff will reappear next sync.
**Option 3 — Skip forever**: Keep local intentional divergence; adds to divergence_acknowledged.
```

Wait for user response before moving to the next file.

On **Accept**: overwrite `hub/<local_path>` with upstream content. Log: `APPLIED: <local_path>`.

On **Skip**: no change. Log: `SKIPPED: <local_path>`.

On **Skip forever**: no change. Add `<rel_path>` to `divergence_acknowledged` list. Log: `ACKNOWLEDGED DIVERGENCE: <local_path>`.

## Step 5: Update sync state

Write `hub/.upstream-sync-state.json`:
```json
{
  "last_sha": "<current HEAD SHA>",
  "last_synced_at": "<ISO-8601 timestamp>",
  "divergence_acknowledged": [<accumulated list including this run's additions>]
}
```

## Step 6: Run sync (if any files accepted)

```bash
./sync.sh --fix
```

## Step 7: Report

```
## Sync Complete

Applied:              N files
Skipped (this time):  M files
Acknowledged forever: K files

Sync state → <sha>
```

If any files were applied: remind user to review fan-out targets and commit:
```bash
git add hub/ && git commit -m "chore: pull awslabs/aidlc-workflows upstream @ <sha-short>"
```
