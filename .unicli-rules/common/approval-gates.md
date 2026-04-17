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
