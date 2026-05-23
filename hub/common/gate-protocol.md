# Gate Protocol — Construction Stages SSOT

All Construction-phase skills MUST follow this protocol. It unifies three concerns:
vague-ambiguity detection → Q-list generation → standardized approval gate.

Related references:
- `common/question-format-guide.md` — Q-list file format (multiple-choice, [Answer]: tags, "Other" mandatory)
- `common/approval-gates.md` — machine-readable audit marker formats

---

## 1. Vague-Keyword Triggers (Q-list mandatory)

After producing the draft artifact, scan for these keywords. If ANY appear and the meaning is not fully determined by prior stage artifacts:

| Trigger word / phrase | Why it signals ambiguity |
|-----------------------|--------------------------|
| `depends`, `depending on` | Decision deferred — needs to be resolved now |
| `maybe`, `might`, `possibly` | Option not committed to |
| `not sure`, `unclear`, `TBD`, `TODO` | Known gap — must surface to user |
| `mix of`, `hybrid`, `combination of` | Trade-off not decided |
| `somewhere between`, `approximately` | Threshold or bound not fixed |
| `standard`, `typical`, `usual`, `similar` | "Standard" for whom? Must specify |
| `and/or`, `etc.`, `등등` | Enumeration is incomplete |

**Action when triggered**: Create `aidlc-docs/construction/{unit}/{stage}-questions.md` per `common/question-format-guide.md` format. Post to user **as a file** (never inline in chat). Wait for all `[Answer]:` tags to be filled before proceeding.

If no vague keywords found: skip Q-list step and proceed directly to the approval gate.

---

## 2. Q-list File Convention

Use `common/question-format-guide.md` for the exact format. Key rules:
- File: `aidlc-docs/construction/{unit}/{stage}-questions.md`
- Each question: multiple-choice A/B/C… + "Other" as the LAST option (MANDATORY)
- Each answer slot: `[Answer]:` tag on its own line
- After user fills answers: read the file, validate completeness, update artifact, then gate

---

## 3. Standardized Approval Gate Message

Every Construction stage MUST use EXACTLY this format after producing its artifact:

```
## {Stage Name} Complete — {Unit Name}

**Artifact(s)**:
- `{path/to/artifact.md}`

{1-3 line summary of what was designed/generated}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change. I will update the artifact and re-present this gate.
**Option 2 — Continue**: Proceed to {next stage name}.
```

**Critical rules**:
- No third option
- The `**STOP**` line is mandatory — do not omit
- Do NOT auto-advance after presenting this gate
- Log the raw user response verbatim to `aidlc-docs/audit.md`

---

## 4. Approval Marker Format

On "Continue" (Option 2), write EXACTLY this to `aidlc-docs/audit.md`:

```
APPROVAL-STAGE: {STAGE_NAME}_APPROVED [unit={unit}]
```

Stage name constants (upper-snake, these are the ONLY valid values):

| Stage | Marker |
|-------|--------|
| Functional Design | `FUNCTIONAL_DESIGN_APPROVED` |
| NFR Requirements | `NFR_REQUIREMENTS_APPROVED` |
| NFR Design | `NFR_DESIGN_APPROVED` |
| Infrastructure Design | `INFRASTRUCTURE_DESIGN_APPROVED` |
| Code Generation Part 1 (plan) | `CODE_GENERATION_PLAN_APPROVED` |
| Code Generation Part 2 (execute) | `CODE_GENERATION_APPROVED` |
| Build and Test | `BUILD_AND_TEST_APPROVED` |

**SKIP marker** (when a conditional stage is skipped):
```
SKIP: {stage display name} — {unit} — {rationale}
```

**Invalid forms** (reject if seen in audit.md — suggest correction to user):
- `*_COMPLETE` — wrong suffix
- `APPROVAL-STAGE: CODE_GENERATION_APPROVED` without `[unit=...]` — missing unit tag

---

## 5. Coordinator Gate Guard (aidlc-workflow enforcement)

Before dispatching any Construction stage skill, the coordinator MUST verify in `aidlc-docs/audit.md`:

1. The **previous** stage has either:
   - `APPROVAL-STAGE: {PREV_STAGE}_APPROVED [unit={unit}]`, OR
   - `SKIP: {prev stage name} — {unit} — ...`
2. If neither found → **block dispatch**; re-display the prior stage's gate message; wait for user response.
3. If `{PREV_STAGE}_COMPLETE` (wrong format) found → ask user "마커 형식 드리프트 발견. _APPROVED로 정정하고 계속할까요?" → on yes: write corrected marker to audit.md, proceed.

**Hard blockers** (never bypass):
- Code Generation Part 2 dispatch requires `CODE_GENERATION_PLAN_APPROVED` in audit.md
- Build and Test dispatch requires `CODE_GENERATION_APPROVED` in audit.md

Scan the **last 40 lines** of audit.md (not the whole file — it's append-only and can be large).
