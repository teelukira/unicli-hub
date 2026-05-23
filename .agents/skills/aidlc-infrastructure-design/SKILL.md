---
name: aidlc-infrastructure-design
description: >-
  Run per-unit AI-DLC Infrastructure Design. Use when the active construction
  unit requires mapping to infrastructure services, deployment architecture
  specification, or cloud resource definition.
allowed-tools: [Read, Edit, Write, Task]
phase: construction
stage: infrastructure-design
per-unit: true
human-clarification: required
plan-creation: false
plan-verification: false
artefact-verification: false
depth: adaptive
---

# AI-DLC Infrastructure Design

**Stage**: Construction — Infrastructure Design (CONDITIONAL, per-unit)
**Gate**: Standardized 2-option approval
**HITL Gate Reference**: `hub/common/gate-protocol.md`

## Prerequisite check (Step 0)

Output depth (Minimal / Standard / Comprehensive) follows `hub/common/depth-levels.md`.

Read `references/state-contract.md`. Identify active unit.

Evaluate Execute-IF / Skip-IF:
- **Execute IF**: Infrastructure services need mapping; deployment architecture required; cloud resources need specification
- **Skip IF**: No infrastructure changes; infrastructure already defined; pure business logic unit

If skip: write skip to audit.md. Mark `[x] Infrastructure Design`. Return.

## Step 1: Log start and load rules

Append to audit.md. Read `hub/construction/infrastructure-design.md`.

## Step 2: Execute infrastructure design

Read functional design and NFR design artifacts.

Per loaded `infrastructure-design.md`:
- Map logical components to AWS infrastructure (ECS/EKS services, RDS, ElastiCache, S3, CloudFront)
- Define Kubernetes/ECS task definitions
- Define Terraform resource specifications
- Define network topology (VPC, subnets, security groups)
- Define Kafka topics and consumer groups
- Define Keycloak realm and client config

Use ASCII diagrams (validated per `references/content-validation.md`).

Output: `aidlc-docs/construction/{unit}/infrastructure-design/`

## Step 3: IaC code generation (if needed)

If new Terraform resources required:
Invoke `codegen-iac` subagent via Task tool (conditional BLOCKING):
```
Task({
  description: "Generate Terraform IaC for {unit}",
  prompt: "Generate Terraform resources for: [list from infra design]. Follow existing infra/ patterns. Output to infra/ directory.",
  subagent_type: "codegen-iac"
})
```

## Step 3b: Vague-Keyword Scan (per gate-protocol.md)

Scan the draft artifact for vague keywords (`depends / maybe / not sure / unclear / TBD / mix of / somewhere between / standard / typical / usual / and/or / etc.`).

- **If found**: Create `aidlc-docs/construction/{unit}/infrastructure-design-questions.md` per `common/question-format-guide.md`. Notify user; wait for all `[Answer]:` tags filled. Update artifact. Then proceed to Step 4.
- **If not found**: Proceed directly to Step 4.

## Step 4: Standardized 2-option gate

```
## Infrastructure Design Complete — {Unit Name}

**Artifact(s)**:
- `aidlc-docs/construction/{unit}/infrastructure-design/`

{Infrastructure diagram and resource list}

**STOP** — Do not proceed until the user explicitly approves.
Approval must be clear and unambiguous.

---
**Continue or Request Changes?**

**Option 1 — Request Changes**: Describe what needs to change. I will update the artifact and re-present this gate.
**Option 2 — Continue**: Proceed to Code Generation.
```

Log raw user input to audit.md. DO NOT PROCEED until user responds.

Mark `[x] Infrastructure Design` and log `APPROVAL-STAGE: INFRASTRUCTURE_DESIGN_APPROVED [unit={unit}]` on "Continue".

