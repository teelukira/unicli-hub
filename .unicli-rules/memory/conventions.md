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
