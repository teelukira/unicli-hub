# AI-DLC Audit Log Format

## Rule: ALWAYS append, NEVER overwrite

- Use Read + Edit/append only. NEVER overwrite audit.md entirely.
- Every stage MUST log to `aidlc-docs/audit.md`.

## Canonical Audit Entry Format

```
## [Stage Name or Interaction Type]
**Timestamp**: [ISO 8601 — YYYY-MM-DDTHH:MM:SSZ]
**User Input**: "[Complete raw user input — never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

## Canonical Machine-Readable Markers

These markers MUST appear literally in audit.md at the appropriate moment. Hooks and the coordinator scan for them.

| Marker | When to write |
|--------|--------------|
| `APPROVAL-STAGE: <STAGE_NAME>_APPROVED` | After user chooses "Continue to Next Stage" |
| `APPROVAL-STAGE: <STAGE_NAME>_CHANGES_REQUESTED` | After user chooses "Request Changes" |
| `GATE-QA: PASS` / `GATE-QA: FAIL` | After qa-tester subagent completes |
| `GATE-TMF: PASS` / `GATE-TMF: FAIL` / `GATE-TMF: N/A` | After tmf-compliance-reviewer completes |
| `GATE-WEB: PASS` / `GATE-WEB: CONDITIONAL PASS` / `GATE-WEB: FAIL` / `GATE-WEB: N/A` | After web-integration-tester completes |
| `JIRA-CREATED: <TICKET_ID>` | After Jira ticket created |
| `JIRA-INPROGRESS: <TICKET_ID>` | After Jira ticket transitioned to In Progress |
| `SKIP: <STAGE_NAME> — <rationale>` | When a CONDITIONAL stage is skipped |

## Subagent Invocation Entry Format

```
## Subagent Invocation — <agent-name>
**Timestamp**: [ISO 8601]
**Input**: "[task description passed to subagent]"
**Result**: PASS | FAIL | CONDITIONAL PASS | N/A
**Context**: [unit, stage, gate type]

---
```

## Mandatory Logging Rules

1. Log EVERY user input with COMPLETE RAW INPUT — never summarize or paraphrase
2. Log every approval prompt BEFORE asking the user
3. Log every user response AFTER receiving it
4. Log every subagent invocation (start + result)
5. Log every CONDITIONAL skip with rationale
6. ISO 8601 timestamps on every entry
