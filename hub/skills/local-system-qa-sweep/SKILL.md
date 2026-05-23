---
name: local-system-qa-sweep
description: >-
  Run an end-to-end QA sweep against the local Docker fullstack — rebuilds and
  starts the stack, exercises every frontend menu and CRUD path via Playwright
  MCP, runs the TMF CTK conformance matrix, validates TMF API spec compliance
  (runtime vs architect vs TMF reference), and reviews SID schema using the TMF
  KB MCP. Records every defect to docs/todos/backlog.md. Use whenever the user
  asks to "run system QA", "sweep the local stack", "test all menus and CRUD",
  "verify CTK", "check TMF spec", "review SID schema", or audit the local
  frontend after a stack rebuild. Accepts mode arg: full | ui | ctk | api | sid
  | quick. Triggers automatically when user says "로컬 QA", "전체 테스트", "메뉴 테스트",
  "CRUD 검증", "CTK 실행", "TMF API 검증", "SID 검토" or similar.
allowed-tools: [Read, Edit, Write, Bash, Task]
phase: operations
stage: qa-sweep
per-unit: false
human-clarification: optional
plan-creation: false
plan-verification: false
depth: adaptive
---

# Local System QA Sweep

**Purpose**: System-wide QA across UI, TMF conformance, API contracts, and SID schema.
**Not** a per-unit build gate (that's `aidlc-build-and-test`). This is an informational sweep that records defects to `docs/todos/backlog.md`.

---

## Step 0 — Parse mode and confirm prerequisites

Parse the first argument (default: `full`). Valid modes:

| Mode | What runs |
|------|-----------|
| `full` | Stack + UI + CTK + API + SID |
| `ui` | Stack + UI sweep only |
| `ctk` | Stack + CTK matrix only |
| `api` | Stack + API contract only |
| `sid` | Stack + SID schema only |
| `quick` | Stack (--no-build) + UI sample (5 menus) |

Confirm Docker/Colima is reachable: `docker info` should exit 0. If not, instruct user to start Colima first (`colima start`) and stop.

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

---

## Step 1 — Generate sweep ID and log to audit

Generate a sweep ID: `QA-SWEEP-<YYYYMMDD>-<HHMM>` (use `date +"%Y%m%d-%H%M"`).

Append to `aidlc-docs/audit.md`:

```
## QA Sweep — <sweep-id>
**Timestamp**: <ISO 8601>
**Mode**: <mode>
**Operator**: local-system-qa-sweep skill
---
```

---

## Step 2 — Bring up the local fullstack

If mode is `quick`:
```bash
./infra/local-fullstack/start.sh -d --no-build
```

Otherwise (all other modes):
```bash
./infra/local-fullstack/start.sh -d
```

Then gate on health:
```bash
WAIT_TIMEOUT=300 bash scripts/lib/wait-for-stack.sh
```

If `wait-for-stack.sh` exits non-zero, record an `INFRA-1` defect in the backlog and **abort the sweep** (the subsequent steps all depend on a running stack). Show the user the container logs for the unhealthy service.

---

## Step 3 — TMF KB MCP pin (modes: full, api, sid)

Skip this step for modes `ui`, `ctk`, `quick`.

Mandatory init order (see `hub/agents/tmf-compliance-reviewer.md`):
1. `mcp__atom-tmf-kb-mcp__tmf_kb_list_releases({})`
2. `mcp__atom-tmf-kb-mcp__tmf_kb_pin({"version": "<latest from step 1>"})` — **must be the first non-list call**
3. `mcp__atom-tmf-kb-mcp__tmf_kb_get_status({})`

Record the pinned version in the sweep summary.

---

## Step 4 — UI sweep via Playwright MCP (modes: full, ui, quick)

Read `references/ui-sweep.md` for the full menu inventory (15 top-level groups, 40+ routes) and CRUD matrix.

For `quick` mode, only exercise sections 1–5 of the menu inventory (Dashboard, Resources, Resource Catalogs, Zones, Topology).

**Drive pattern** (execute for each menu group):
1. `mcp__playwright__browser_navigate({"url": "http://localhost:3000/<route>"})`
2. `mcp__playwright__browser_snapshot({})` — verify the page renders without blank/500
3. For menus with CRUD: follow the create → read → update → delete steps in `references/ui-sweep.md`
4. Save a screenshot on failure: `mcp__playwright__browser_take_screenshot({"path": "docs/todos/qa-screenshots/<sweep-id>/<menu>-fail.png"})`

Cross-reference `scripts/verify/playwright-mcp-checklist.md` for per-service API assertions (U02/U03/U04/U08/U09/U10/U21 + FE nav checks). The checklist documents known issues (INF-2 enum casing, FE-1/FE-2 nginx proxy gaps) — do not record these as new defects.

Classify defects as:
- `UI-*` — page fails to render, navigation broken, button doesn't respond
- `CRUD-*` — create/read/update/delete returns 4xx/5xx or produces wrong data

---

## Step 5 — CTK conformance matrix (modes: full, ctk)

Read `references/ctk-runbook.md` for command reference and pass-rate thresholds.

```bash
./scripts/run-tmf-ctk.sh --all
REPORT_DIR=$(ls -td scripts/tmf-ctk/reports/*/ | head -1)
python3 scripts/aggregate-ctk-reports.py "$REPORT_DIR"
```

Parse `"$REPORT_DIR/summary.md"` for:
- Units that fell below their `min_assertion_pass_rate` threshold → `CTK-*` defects (P1 if >5% below, P2 if marginal)
- Units at 100% → mark as pass, no defect

---

## Step 6 — API contract validation (modes: full, api)

Read `references/api-contract.md` for the three-way diff logic and service registry.

```bash
./scripts/validate-api-contract.sh --mode all
REPORT=$(ls -td specs/tmf/api-contract/*/ | head -1)/summary.md
```

Parse `$REPORT` for contract deviations. Also run Spectral lint if available:
```bash
npx spectral lint specs/tmf/u*/api-spec.yaml --ruleset scripts/.spectral.yaml 2>/dev/null || true
```

Classify deviations as `API-*` defects (P1 = missing required field / wrong HTTP status; P2 = response schema mismatch; P3 = naming/casing drift).

---

## Step 7 — SID schema review (modes: full, sid)

Read `references/sid-schema.md` for the cross-check procedure.

```bash
python3 scripts/validate-sid-schema.py
REPORT=$(ls -t specs/tmf/sid-schema/report-*.md | head -1)
```

Then supplement with KB MCP cross-check for Resource domain ABEs:

```
mcp__atom-tmf-kb-mcp__tmf_kb_get_domain_landscape({"domain": "Resource"})
```

For each entity flagged in the script report, call:
```
mcp__atom-tmf-kb-mcp__tmf_kb_judge({"candidate_id": "<entity>", "reverse_feature": "<attribute>"})
```

to verify attribute fidelity against MODA 25.5. Record divergences as `SID-*` defects (P1 = mandatory ABE attribute missing; P2 = type mismatch; P3 = optional attribute / naming deviation).

---

## Step 8 — Investigate non-trivial failures with aidlc-researcher

For each defect that is:
- Not a documented known issue (INF-2, FE-1, FE-2 from `scripts/verify/playwright-mcp-checklist.md`)
- Not trivially self-explanatory (e.g., a 404 on a missing route)

Dispatch a research task:

```
Task({
  description: "Root-cause investigation: <defect-id> — <one-line description>",
  prompt: "You are the aidlc-researcher agent. Investigate this QA failure: <defect-id>. Context: <paste the failure output>. Consult project docs, source code under <relevant service dir>, and TMF KB MCP if relevant. Write your findings to docs/research/qa-sweep-<sweep-id>-<topic-slug>.md using the standard research frontmatter (title, unit, topic, date, confidence). Return a 3-sentence summary.",
  subagent_type: "aidlc-researcher"
})
```

Research agents run concurrently when there are multiple failures; collect all summaries before proceeding to backlog writeback.

---

## Step 9 — Write defects to backlog

Read `references/backlog-writeback.md` for the ID scheme, priority taxonomy, and append rules.

Append a new section to `docs/todos/backlog.md` above the existing `🟢 Low / Cosmetic` section:

```markdown
## 🟡 QA Sweep <sweep-id> — <YYYY-MM-DD>

**Scope**: <mode>  **Healthy containers**: <X>/18  **Duration**: <elapsed>
**Evidence**:
- UI screenshots: `docs/todos/qa-screenshots/<sweep-id>/`
- CTK reports: `scripts/tmf-ctk/reports/<REPORT_DIR>/`
- API contract: `specs/tmf/api-contract/<UTC>/summary.md`
- SID schema: `specs/tmf/sid-schema/report-<UTC>.md`
- Research notes: `docs/research/qa-sweep-<sweep-id>-*.md`

| ID | 우선순위 | 내용 | 상태 |
|----|---------|------|------|
| **<defect-id>** | P1/P2/P3 | <Korean or English description> — evidence link | open |
```

If zero defects were found, add a single row: `| <sweep-id>-OK | — | 전체 PASS — 결함 없음 | done |`

After appending, update `docs/todos/README.md` to add a row referencing the new sweep section.

---

## Step 10 — Output summary to user

Print a concise sweep report:

```
## QA Sweep <sweep-id> complete

Mode: <mode> | Elapsed: <time>
Containers: <X>/18 healthy

Defects found:
  P1 (blocking):  <N>
  P2 (spec diff): <N>
  P3 (cosmetic):  <N>

Top 3 recommended next actions:
  1. <highest-severity defect + suggested owner/service>
  2. ...
  3. ...

Full backlog entry: docs/todos/backlog.md#qa-sweep-<sweep-id>
Research notes: docs/research/qa-sweep-<sweep-id>-*.md (if any)
```

Do **not** invoke the standardized 2-option HITL approval gate — this sweep is informational. The user decides which defects to act on.
