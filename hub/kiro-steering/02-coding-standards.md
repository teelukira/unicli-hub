# Coding Standards

## Code Style

- Comments: **default to none**. Add a single line only when the *why* is non-obvious.
- Prefer explicit, self-documenting names over comments.

## Test Policy

- Frontend E2E: local-server (Playwright `webServer`) is mandatory for
  frontend units' Build and Test gate.

## Security

- Secrets: `.env` or secret manager — never commit.
- User input is validated at boundaries; trust internal code.

## Framework Conventions

- Edit canonical files under `hub/` or `.unicli-hub/templates/`.
- Do not edit generated targets directly.
- After changes, run `./sync.sh --fix` then `./sync.sh --check`.
