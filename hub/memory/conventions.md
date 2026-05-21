---
name: conventions
description: Project-wide code and documentation conventions for AI CLIs.
type: memory
---

# Conventions

Project-wide code and documentation conventions live here. AI CLIs generating or editing code must honor them.

## Code Style

- Comments: **default to none**. Add a single line only when the *why* is non-obvious.

## Test Policy

- Frontend E2E: local-server (Playwright `webServer`) is mandatory for
  frontend units' Build and Test gate. Mock-based or backend-skipped E2E
  does not satisfy this requirement.

## Security

- Secrets: `.env` or secret manager — never commit.
- User input is validated at boundaries; trust internal code.
