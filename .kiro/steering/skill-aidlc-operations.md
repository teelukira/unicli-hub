---
name: aidlc-operations
description: >-
  AI-DLC Operations placeholder. Use after all Construction units are complete
  and Build and Test has passed. This is a placeholder stage for future
  deployment and monitoring workflows.
allowed-tools: [Read, Edit, Write]
---

# AI-DLC Operations

**Stage**: Operations Phase (PLACEHOLDER)
**Gate**: None

## Status

This stage is a placeholder for future expansion.

When invoked, display:

```
## Operations Phase

All Construction units are complete.

This phase is currently a placeholder. Future expansion will include:
- Deployment planning and execution
- Monitoring and observability setup
- Incident response procedures
- Maintenance and support workflows
- Production readiness checklists

**Current state**: All per-unit build/test/QA/TMF verification is handled in the Construction phase.

For deployment guidance, refer to:
- `infra/local-fullstack/start.sh` — local Docker fullstack
- `infra/dev-light/` — AWS ECS Fargate dev-light deployment
- `infra/` Terraform — production EKS deployment
```

Log to audit.md:
```
## Operations Phase
**Timestamp**: [ISO 8601]
**User Input**: "[user request]"
**AI Response**: "Operations placeholder displayed."
**Context**: Operations Phase — All construction units complete
---
```

