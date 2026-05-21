---
name: core-workflow
description: AI-assisted software development workflow template. Customize stages and depth for your project.
type: workflow
---

# Core Workflow

## Adaptive Workflow Principle

The workflow adapts to the work, not the other way around.
AI assesses which stages are needed based on user intent, codebase state, complexity, and risk.
Stages marked `ALWAYS` run every time; `CONDITIONAL` stages run only when the assessment warrants.

---

## 🔵 INCEPTION PHASE

**Purpose**: Planning, requirements gathering, architectural decisions.

**Focus**: Determine WHAT to build and WHY.

### Workspace Detection (`ALWAYS`)

Detect project state (greenfield vs. brownfield) and resume from prior session if applicable.

### Reverse Engineering (`CONDITIONAL` — brownfield only)

Analyze existing codebase to produce architecture, API, and component documentation.

### Requirements Analysis (`ALWAYS`)

Gather functional and non-functional requirements. Depth adapts: `minimal` / `standard` / `comprehensive`.

### User Stories (`CONDITIONAL`)

Generate user stories and personas when new user-facing features are involved.

### Workflow Planning (`ALWAYS`)

Produce a Mermaid workflow diagram. Determine which construction stages to execute per unit.

### Application Design (`CONDITIONAL`)

Define new components, service layers, and dependencies when new services are required.

### Units Generation (`CONDITIONAL`)

Decompose the system into ordered units of work when multi-service coordination is needed.

---

## 🟢 CONSTRUCTION PHASE

**Purpose**: Detailed design, NFR implementation, code generation.

**Focus**: Determine HOW to build it.

Per-unit loop (repeat for each unit):

### Functional Design (`CONDITIONAL`)

Data models, business logic, business rules.

### NFR Requirements (`CONDITIONAL`)

Performance, security, scalability.

### NFR Design (`CONDITIONAL`)

NFR patterns and cross-cutting concerns.

### Infrastructure Design (`CONDITIONAL`)

Cloud resources, deployment architecture.

### Code Generation (`ALWAYS`)

Two-part: plan (with checkboxes, get approval) → execute (generate code + tests).

### Build and Test (`ALWAYS`)

Run `qa-tester` (BLOCKING), `tmf-compliance-reviewer` (if TMF unit), `web-integration-tester` (if frontend).

---

## 🟡 OPERATIONS PHASE

**Purpose**: Deployment, monitoring, incident response.

**Status**: Placeholder — expand for your project's operational runbooks.

---

## Key Principles

- Only execute stages that add value
- Log every user input and AI response in `aidlc-docs/audit.md` (append-only)
- Validate Mermaid and ASCII diagrams before writing
- Never edit derived files (`.claude/`, `.cursor/`, `.gemini/`, etc.) — edit `hub/` instead
