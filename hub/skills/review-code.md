---
name: review-code
description: >
  Skill: review-code
allowed-tools: [Read, Bash]
---


## When to Use

- Reviewing a pull / merge request before merge.
- Spot-checking a codegen subagent's output.
- Validating a refactor didn't introduce regressions.

## Prerequisites

- The diff or list of changed files.
- `{RULES_DIR}/common/conventions.md` — project conventions.
- `{RULES_DIR}/common/codegen-principles.md` — code quality baseline.
- `{ADR_INDEX}` — to verify decisions are ADR-compliant.

## Steps

### 1. Gather the diff

```bash
git diff {BASE_BRANCH}..{HEAD_BRANCH} -- {SCOPE_PATHS}
```

Or read specific files if the diff is already known.

### 2. Correctness

- Does the implementation match the stated requirement?
- Are edge cases handled (null / empty / boundary values)?
- Does error handling use the project's standard error shape?

### 3. Test coverage

- Is there a test for every new behaviour?
- Do the tests follow Red → Green → Refactor discipline?
- Are tests isolated (no shared mutable state between tests)?
- If PBT is enabled: is there a property-based test for invariants?

### 4. Architecture / layer compliance

- Are layer boundaries respected (e.g. no framework imports in `{DOMAIN_LAYER}`)?
- Is the change in the correct module / package?
- Does it follow the patterns defined in `{RULES_DIR}/common/architecture.md`?

### 5. ADR compliance

- Scan `{ADR_INDEX}` for ADRs covering the changed files.
- Confirm the change follows every `Accepted` ADR that applies.
- Flag any deviation as a blocking finding.

### 6. Security

- Is all user input validated at the boundary?
- Are secrets handled via environment / secret manager (never hardcoded)?
- Are there any obvious injection or auth bypass risks?

### 7. Performance

- Any N+1 query patterns?
- Any unbounded loops or large in-memory collections?
- Any blocking I/O on a thread that should be async?

### 8. Style and conventions

- Naming follows `{RULES_DIR}/common/conventions.md`.
- Comments explain *why*, not *what*.
- No dead code or commented-out blocks.

### 9. Produce the review report

```markdown
## Code Review — {PR_OR_FEATURE_TITLE}

**Overall**: ✅ Approve / ⚠️ Approve with Nits / ❌ Request Changes

### Blocking findings
- {FILE}:{LINE} — {issue} — {required fix}

### Non-blocking nits
- {FILE}:{LINE} — {suggestion}

### ADR compliance
- ADR-{NUM}: ✅ Compliant / ❌ Deviation — {details}

### Test coverage
- Unit tests: ✅ / ❌ {gap}
- Integration tests: ✅ / ❌ {gap}
- PBT: ✅ / N/A

### Security
- {finding or "No issues found"}

### Recommended follow-ups
- {optional future improvement}
```

## Output

- Review report in the format above.
- Blocking findings must be fixed before merge.
- Nits are optional improvements.

## Guard

- Never approve code with failing tests or compiler errors.
- Never approve hardcoded secrets.
- Never skip the ADR compliance check.
- Raise concerns — do not silently accept deviations from conventions.