# Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work through two integrated parts:
- **Part 1 - Planning**: Create detailed code generation plan with explicit steps
- **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

## ADR Awareness (MANDATORY)

Generated code **MUST conform to** all `Accepted` / `Accepted (Retroactive)` ADRs that affect the current unit.

1. **Pre-generation**: Before writing code, fetch the list of relevant ADRs from `aidlc-docs/construction/{unit}/INDEX.md` `**Relates-To-ADR**:` line. If missing, derive from [`aidlc-docs/index/adr-index.md`](../../aidlc-docs/index/adr-index.md) "Affects-Units 역참조".
2. **Apply during generation**:
   - Architecture decisions (e.g., [ADR-0005 hexagonal 4-module](../../aidlc-docs/adr/cross-cutting/0005-hexagonal-4-module-layout.md), [ADR-0006 Spring Boot 3.4](../../aidlc-docs/adr/cross-cutting/0006-spring-boot-3.4-baseline.md)) constrain module layout, dependencies, and patterns.
   - Domain decisions (e.g., [ADR-0019 IPAM scope](../../aidlc-docs/adr/microservices/0019-ipam-service-domain-scope.md)) constrain bounded context.
   - TMF compliance decisions (e.g., [ADR-0001 NC waive](../../aidlc-docs/adr/tmf-compliance/0001-tmf-nc-waive-policy.md)) define allowed deviations.
3. **New decision during generation**: If generation requires a new architectural decision (e.g., choosing a library not yet covered), STOP, invoke `adr-curator`, then resume.
4. **Cite in plan**: Code generation plan (Part 1) MUST list `Relates-To-ADR: ...` and confirm constraint adherence.

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

## Prerequisites
- Unit Design Generation must be complete for the unit
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for code generation

---

# PART 1: PLANNING

## Step 1: Analyze Unit Context
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Validate unit is ready for code generation

## Step 2: Create Detailed Unit Code Generation Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never aidlc-docs/)
- [ ] Create explicit steps for unit generation:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Unit Testing
  - Business Logic Summary
  - API Layer Generation
  - API Layer Unit Testing
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Unit Testing
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Unit Testing (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts
  - Database entities owned by this unit
  - Service boundaries and responsibilities

## Step 4: Create Unit Plan Document
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story traceability
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the unit code generation plan to the user
- [ ] Highlight unit generation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log Approval Prompt
- [ ] Before asking for approval, log the prompt with timestamp in `aidlc-docs/audit.md`
- [ ] Include reference to the complete unit code generation plan
- [ ] Use ISO 8601 timestamp format

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the unit code generation plan
- [ ] Approval must cover the entire plan and generation sequence
- [ ] If user requests changes, update the plan and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text
- [ ] Mark the approval status clearly
- [ ] When the user approves final Code Generation stage completion, append exact marker: `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit-name}]`

## Step 8.5: Jira ticket presence (MANDATORY — Jira Integration)

**Load** `common/jira-integration.md` §2 (Create Ticket) and duplicate-prevention note at §2 opening.

- [ ] `aidlc-state.md`에서 현재 unit의 `**Jira Ticket**` 확인
- [ ] 이미 실제 키가 있으면: 새 이슈 생성 금지 — `audit.md`에 `JIRA-REUSE: <KEY> [unit={unit-name}]` 기록 후 다음 단계로
- [ ] 키가 비어 있거나 placeholder만 있으면: **Create Story** 절차 전체 실행
  - [ ] Config 로드: `memory/jira-config.local.md` (있으면 우선) → `memory/jira-config.md` (기본값)
  - [ ] Discovery 실행 (config의 `epic_key` 또는 `transition_id_inprogress` 비어있을 때)
  - [ ] Jira 이슈 JSON preview + **명시적 승인** (`common/approval-gates.md`)
  - [ ] Summary: `[{unit-name}] {unit-title}`
  - [ ] Description: `scripts/render-ai-dlc-remote-templates.py`로 `.unicli-rules/templates/remotes/jira-issue.body.md` 렌더 (requirements / execution-plan / code-generation-plan 경로, `approved_at`, reporter, assignee 값 JSON으로 전달)
  - [ ] 승인 직후 `audit.md`에 `APPROVAL-JIRA-CREATE: granted [unit={unit-name}]`
  - [ ] `jira_create_issue` 호출 후 `JIRA-CREATED: ... [unit={unit-name}]` 및 state 갱신
- [ ] **Blocking rule**: 실제 `JIRA-CREATED` + state의 실제 키, 또는 `JIRA-WAIVER`, 또는 (reuse 경로) `JIRA-REUSE` + 기존 실제 키. `TODO-NWAE-*` 단독으로는 Code Generation 완료 불가

## Step 9: Update Progress
- [ ] Mark Code Generation Part 1 (Planning) complete in `aidlc-state.md`
- [ ] Update the "Current Status" section
- [ ] Prepare for transition to Code Generation

## Step 9.5: Transition Jira Story to In Progress (Jira Integration)

**Load** `common/jira-integration.md` and execute the **Transition** procedure.

- [ ] `aidlc-state.md`에서 현재 unit의 `**Jira Ticket**` 값 읽기
- [ ] `TODO-NWAE-` 패턴이면: skip + audit.md에 `JIRA-RECONCILE-NEEDED` 기록 (비blocking)
- [ ] 실제 `NWAE-###`이면: `jira_transition_issue(issue_key, transition_id_inprogress)` 호출
- [ ] 실패 시: audit.md 기록 후 계속 (비blocking)
- [ ] 성공 시 `aidlc-docs/audit.md`에 exact marker 추가: `JIRA-INPROGRESS: NWAE-### [unit={unit-name}]`
- [ ] **Blocking rule**: Code Generation stage를 완료 처리하거나 Build and Test로 진행하기 전에 `JIRA-INPROGRESS: NWAE-### [unit={unit-name}]` 또는 명시적 `JIRA-WAIVER`가 반드시 존재해야 함

---

# PART 2: GENERATION

## Step 10: Load Unit Code Generation Plan
- [ ] Read the complete plan from `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (unit, dependencies, stories)

## Step 10.5: Invoke Specialized Code Generation Subagent (MANDATORY — BLOCKING)

**CRITICAL**: The main model MUST NOT write production code directly. Use the Agent tool with the matching `subagent_type` below. Acting as the subagent role yourself is **prohibited**.

All dispatched codegen subagents MUST follow `common/codegen-principles.md` (Karpathy 4 원칙 + Kent Beck TDD R→G→R). 위반 발견 시 메인 모델은 fix-request로 **같은 서브에이전트를 재호출**한다 — 메인 모델 직접 수정 금지.

Based on the unit's primary stack (declared in NFR Requirements / tech-stack-decisions.md):

| Stack signature | subagent_type |
|----------------|---------------|
| Java + Spring Boot 3.x backend | `codegen-backend` |
| Flyway / PostgreSQL / JPA schema | `codegen-db` |
| React 18 + TypeScript frontend | `codegen-frontend` |
| Terraform / IaC | `codegen-iac` |
| Polyglot unit | Invoke each matching subagent in sequence: `codegen-db` → `codegen-backend` → `codegen-frontend` → `codegen-iac` |

**Pre-flight**:
1. Confirm `tech-stack-decisions.md` exists and lists the chosen stack.
2. Pass the unit's code generation plan path + the workspace root + the "확정 변경 영역" list to the subagent.
3. **Blocking**: Do not proceed to Step 11 until the subagent reports completion.

**Audit** — append to `aidlc-docs/audit.md` after each subagent completes:
```
## Subagent Invocation — codegen-<stack>
**Timestamp**: [ISO 8601]
**Stage**: Code Generation
**Unit**: [unit-name]
**Purpose**: Code production for [stack]
**Result**: [PASS / summary]
---
```

**Failure handling**: If a subagent reports it cannot proceed (missing context, conflict, etc.), surface the issue to the user before retrying — do **NOT** silently fall back to direct main-model code generation.

After every codegen subagent completes, append the **Codegen Principles Compliance** entry (format defined in `common/codegen-principles.md`) to `aidlc-docs/audit.md`.

---

## Step 10.6: Principles Review Gate (BLOCKING)

Before proceeding to Step 11, the main model MUST verify the dispatched subagent's output against `common/codegen-principles.md`. This gate is the main model's responsibility — the subagent cannot audit itself.

- [ ] Confirm the Codegen Principles Compliance audit entry exists in `aidlc-docs/audit.md`
- [ ] Verify P1 (Think Before Coding): no silent assumptions in generated code; ambiguities were surfaced before implementation
- [ ] Verify P2 (Simplicity First): no speculative abstractions, no unrequested features, no impossible-scenario error handling
- [ ] Verify P3 (Surgical Changes): changed files are all within the plan's "확정 변경 영역"; no style-preference rewrites of untouched code
- [ ] Verify P4 (Goal-Driven Execution): each generated method has at least one corresponding test that defines its success criterion

**If any check fails**:
1. Do NOT proceed to Step 11
2. Write a targeted `fix-request-{unit}-principles.md` describing the specific violation
3. Re-invoke the same codegen subagent with `Use the Agent tool with subagent_type: "<name>"`, passing the fix-request path
4. Repeat Step 10.6 after the re-invocation completes

**Do NOT** fix principle violations directly in the main model — this gate exists precisely to keep code generation delegated to the correct subagent.

---

## Step 11: Execute Current Step
- [ ] Verify target directory from plan (never aidlc-docs/)
- [ ] **Brownfield only**: Check if target file exists
- [ ] Generate exactly what the current step describes:
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: Workspace root per project structure
  - **Documentation**: `aidlc-docs/construction/{unit-name}/code/` (markdown only)
  - **Build/Config Files**: Workspace root
- [ ] Follow unit story requirements
- [ ] Respect dependencies and interfaces

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the unit code generation plan
- [ ] Mark associated unit stories as [x] when their generation is finished
- [ ] Update `aidlc-docs/aidlc-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Continue or Complete Generation
- [ ] If more steps remain, return to Step 10
- [ ] If all steps complete, proceed to present completion message

## Step 14: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `aidlc-docs/construction/[unit-name]/code/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the generated code based on your review
> ✅ **Continue to Next Stage** - Approve code generation and proceed to **[next-unit/Build & Test]**

---
```

## Step 15: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the generated code
- Approval must be clear and unambiguous
- If user requests changes, update the code and repeat the approval process

## Step 16: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark Code Generation stage as complete for this unit in aidlc-state.md
- **Do not** mark Code Generation complete until all of the following exist in `aidlc-docs/audit.md`:
  - `APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit-name}]`
  - `APPROVAL-JIRA-CREATE: granted [unit={unit-name}]` or `JIRA-WAIVER: approved-by-user [unit={unit-name}] reason=...` or `JIRA-REUSE: <KEY> [unit={unit-name}]` (reuse path: ticket created earlier, e.g. Requirements Analysis)
  - `JIRA-CREATED: NWAE-### [unit={unit-name}]` or `JIRA-WAIVER: approved-by-user [unit={unit-name}] reason=...`
  - `JIRA-INPROGRESS: NWAE-### [unit={unit-name}]` or `JIRA-WAIVER: approved-by-user [unit={unit-name}] reason=...`

---

## Critical Rules

### Code Location Rules
- **Application code**: Workspace root only (NEVER aidlc-docs/)
- **Documentation**: aidlc-docs/ only (markdown summaries)
- **Read workspace root** from aidlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `lib/`, `pkg/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- Document unit context and dependencies
- Get explicit user approval before generation

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark unit stories [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit code generation plan created and approved
- All steps in unit code generation plan marked [x]
- All unit stories implemented according to plan
- All code and tests generated (tests will be executed in Build & Test phase)
- Deployment artifacts generated
- Complete unit ready for build and verification
