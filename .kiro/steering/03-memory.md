# Project Facts

> **Template.** Fill in the real project facts. Leaving vague "TBD" values actively hurts AI output — be specific or delete the section.

## Team / Owner

- _TBD — responsible team or individual, Slack channel, issue tracker._

## Repository

- Primary repo: _TBD_
- Branching model: _TBD (trunk-based, gitflow, ...)_
- Default branch: `main`

## Core Decisions

- _TBD — irreversible technical choices and the reason behind them (one line each)._
- _Example: "Chose DynamoDB over PostgreSQL because of latency SLA."_

## Environments

- _TBD — dev / staging / prod endpoints and how each is deployed._

## Stakeholders

- _TBD — owners of external interfaces, reviewers._

# Conventions

Project-wide code and documentation conventions live here. AI CLIs generating or editing code must honor them.

## Naming

- File names: _TBD (kebab-case / snake_case / ...)_
- Functions: _TBD (camelCase / snake_case)_
- Constants: _TBD (UPPER_SNAKE_CASE)_
- Tests: `<module>.test.*` or `test_<module>.*`

## Directory Layout

- Source: `src/`
- Tests: `tests/` or co-located with source
- Docs: `docs/`

## Commit Messages

- Style: _TBD (e.g., Conventional Commits)_
- Issue references: _TBD_

## Code Style

- Linter: _TBD (eslint, ruff, golangci-lint, ...)_
- Formatter: _TBD (prettier, black, gofmt, ...)_
- Max line length: _TBD_
- Comments: **default to none**. Add a single line only when the *why* is non-obvious.

## Test Policy

- _TBD — coverage targets, mandatory case categories._
- Mock policy: _TBD_

## Security

- Secrets: `.env` or secret manager — never commit.
- User input is validated at boundaries; trust internal code.

# Glossary

Keep project-specific terminology here. Any word that is used with a meaning different from plain English must be recorded.

| Term | Definition | Note |
|------|------------|------|
| _TBD_ | _TBD_ | _TBD_ |

## Abbreviations

| Abbreviation | Full | Context |
|--------------|------|---------|
| _TBD_ | _TBD_ | _TBD_ |


