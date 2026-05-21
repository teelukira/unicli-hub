# hub/common — Shared Rule Detail Files

Place shared rule files here that multiple AI CLIs can reference.

Typical contents:
- `process-overview.md`  — workflow overview
- `conventions.md`       — coding conventions
- `architecture.md`      — architecture decisions
- `tech-stack.md`        — technology stack guide

These files are referenced from `hub/core-workflow.md` and individual skill/agent files.
They are not fanned out automatically — they are read from `hub/common/` directly.
