# Approval Gates

Actions that must not run without **explicit user approval**. All CLIs share this policy.

## Hard prohibitions (warn and confirm even on explicit instruction)

- Mass deletion like `rm -rf`
- `git push --force`, especially to `main` / `master`
- DDL or DELETE statements against the production database
- Committing secrets (`.env`, credentials, tokens) to a public repository

## Requires approval (ask before acting)

- Deleting files (5+ files, or an entire directory)
- Adding, removing, or upgrading dependencies
- Git operations: `push`, `merge`, `rebase`, `reset --hard`, `branch -D`
- Sending to remote systems: Slack, email, Jira, GitHub (PR / issue), external APIs
- Database schema changes
- CI/CD configuration changes

## Auto-allowed (no approval needed)

- Local file edits (create / modify)
- Running builds, tests, and lints
- Local Git: `status`, `diff`, `log`, `add`, local `commit`
- Read-only queries (files, HTTP GETs)

## Principle

> *Measure twice, cut once.* For destructive actions, always consider a reversible alternative first.

## Machine-Readable Audit Markers

Hooks enforce stage advancement and Jira workflow using exact audit markers in `aidlc-docs/audit.md`.
When a stage or remote action is approved, record the corresponding marker verbatim:

- `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit=u23]`
- `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit=u23]`
- `APPROVAL-JIRA-CREATE: granted [unit=u23]`
- `JIRA-CREATED: NWAE-123 [unit=u23]`
- `JIRA-INPROGRESS: NWAE-123 [unit=u23]`
- `GATE-QA: PASS [unit=u23]`
- `GATE-TMF: PASS [unit=u23]` or `GATE-TMF: N/A [unit=u23]`
- `GATE-WEB: PASS [unit=u23]`, `GATE-WEB: CONDITIONAL PASS [unit=u23]`, or `GATE-WEB: N/A [unit=u23]`

If the user explicitly waives a Jira or gate requirement, log an exact waiver marker:

- `JIRA-WAIVER: approved-by-user [unit=u23] reason=<short-reason>`
- `GATE-WAIVER: approved-by-user [unit=u23] reason=<short-reason>`

These markers are intended for deterministic hook checks. Do not paraphrase them.
