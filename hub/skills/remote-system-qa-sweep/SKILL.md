---
name: remote-system-qa-sweep
description: >-
  Run an end-to-end QA sweep against a remote AWS web environment (ALB) — 
  exercises every frontend menu and CRUD path via Playwright MCP, and optionally 
  runs TMF CTK, API spec, and SID schema validation if the remote API endpoints 
   are reachable via the ALB. Records every defect to docs/todos/backlog.md. 
  Use whenever the user asks to "run remote QA", "sweep AWS environment", 
  "test ALB URL", or "inspect remote web". Accepts target_url and mode args.
  Triggers automatically when user says "AWS QA", "리모트 테스트", "ALB 검증", 
  "원격 QA" or similar.
allowed-tools: [Read, Edit, Write, Bash, Task]
phase: operations
stage: qa-sweep
per-unit: false
human-clarification: optional
plan-creation: false
plan-verification: false
depth: adaptive
---

# Remote System QA Sweep

**Purpose**: System-wide QA across UI, TMF conformance, API contracts, and SID schema on a remote AWS environment.
**Informational**: Records defects to `docs/todos/backlog.md` with "REMOTE" environment tag.

---

## Step 0 — Parse arguments and confirm reachability

Parse arguments:
1. `target_url` (default: `https://tgo-dev-alb-standalone-99090405.ap-northeast-2.elb.amazonaws.com/`)
2. `mode` (default: `full`). Valid modes: `full | ui | ctk | api | sid | quick`.

Confirm the `target_url` is reachable:
```bash
curl -Is --connect-timeout 5 "<target_url>" | head -n 1
```
If unreachable, inform the user and ask if they want to proceed (maybe it's a VPN issue or internal ALB).

---

## Step 1 — Generate sweep ID and log to audit

Generate a sweep ID: `QA-REMOTE-<YYYYMMDD>-<HHMM>` (use `date +"%Y%m%d-%H%M"`).

Append to `aidlc-docs/audit.md`:

```
## QA Remote Sweep — <sweep-id>
**Timestamp**: <ISO 8601>
**Target URL**: <target_url>
**Mode**: <mode>
**Operator**: remote-system-qa-sweep skill
---
```

---

## Step 2 — TMF KB MCP pin (modes: full, api, sid)

Skip this step for modes `ui`, `ctk`, `quick`.

Mandatory init order:
1. `mcp__atom-tmf-kb-mcp__tmf_kb_list_releases({})`
2. `mcp__atom-tmf-kb-mcp__tmf_kb_pin({"version": "<latest from step 1>"})`
3. `mcp__atom-tmf-kb-mcp__tmf_kb_get_status({})`

---

## Step 3 — UI sweep via Playwright MCP (modes: full, ui, quick)

Read `references/ui-sweep.md` for the menu inventory. **Replace `http://localhost:3000` with `<target_url>`**.

For `quick` mode, only exercise sections 1–5 of the menu inventory.

**Drive pattern**:
1. `mcp__playwright__browser_navigate({"url": "<target_url>/<route>"})`
2. `mcp__playwright__browser_snapshot({})`
3. For menus with CRUD: follow the steps in `references/ui-sweep.md`
4. Save a screenshot on failure: `mcp__playwright__browser_take_screenshot({"path": "docs/todos/qa-screenshots/<sweep-id>/<menu>-fail.png"})`

**Note**: If the remote environment uses SSO (e.g., Keycloak, AWS Cognito), the first `navigate` might redirect to a login page. If detected, ask the user for credentials or instructions, or try to bypass if it's a "Click to Login" pattern.

---

## Step 4 — Remote CTK / API / SID (modes: full, ctk, api, sid)

These steps require the remote environment to expose TMF APIs. 
The ALB typically proxies `/api/v1/*` to the respective microservices.

**CTK Strategy**:
Set `CTK_BASE_URL_<UNIT>` environment variables to the remote paths.
Example: `CTK_BASE_URL_U02_TMF639_NEWMAN="<target_url>/api/v1/resource-inventory"`

Run CTK:
```bash
./scripts/run-tmf-ctk.sh --all
```

**API/SID Strategy**:
If scripts `validate-api-contract.sh` and `validate-sid-schema.py` support a `--url` or `--endpoint` flag (or env var), use it. Otherwise, perform a manual inspection of a sample API response from the ALB.

---

## Step 5 — Investigate and Backlog

Follow Steps 8 and 9 from `local-system-qa-sweep/SKILL.md`.
- Label defects as `REMOTE-UI-*`, `REMOTE-API-*`, etc.
- Mention the Environment (Remote/ALB) in the backlog description.

---

## Step 6 — Output summary to user

Print a concise report:

```
## Remote QA Sweep <sweep-id> complete

Target: <target_url>
Mode: <mode> | Elapsed: <time>

Defects found:
  P1: <N> | P2: <N> | P3: <N>

Top Recommended Actions:
  1. <defect + remote context>
  2. ...

Full backlog entry: docs/todos/backlog.md#qa-sweep-<sweep-id>
```
