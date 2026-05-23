# Application Design - Detailed Steps

## Purpose
**High-level component identification and service layer design**

Application Design focuses on:
- Identifying main functional components and their responsibilities
- Defining component interfaces (not detailed business logic)
- Designing service layer for orchestration
- Establishing component dependencies and communication patterns

**Note**: Detailed business logic design happens later in Functional Design (per-unit, CONSTRUCTION phase)

## ADR Awareness (MANDATORY)

This stage typically introduces decisions that match ADR trigger criteria (see `common/adr-conventions.md`): new components, bounded contexts, service boundaries, integration patterns. Before completing this stage:

1. **Consult**: Read [`aidlc-docs/index/adr-index.md`](../../aidlc-docs/index/adr-index.md) — especially the `cross-cutting/`, `microservices/`, `frontend/` categories.
2. **Cite**: Application design output (`aidlc-docs/inception/application-design/*.md`) MUST list `Relates-To-ADR: [NNNN, ...]` near the top when the design reflects existing decisions.
3. **Draft new ADR**: For genuinely new architectural decisions (new microservice, new bounded context, new integration pattern), invoke `adr-curator` subagent before finalizing the design. Do not embed the decision body in design docs — link to the ADR.
4. **Verify**: New ADR file must exist in `aidlc-docs/adr/{category}/NNNN-slug.md` before this stage's approval gate.

## Prerequisites
- Workspace Detection must be complete
- Requirements Analysis recommended (provides functional context)
- User Stories recommended (user stories guide design decisions)
- Execution plan must indicate Application Design stage should execute

## Step-by-Step Execution

### 1. Analyze Context
- Read `aidlc-docs/inception/requirements/requirements.md` and `aidlc-docs/inception/user-stories/stories.md`
- Identify key business capabilities and functional areas
- Determine design scope and complexity

### 1.5. aidlc-researcher Pattern Research (CONDITIONAL)

**Condition**: Invoke when designing NEW components or services where reference architecture patterns, best practices, or third-party library recommendations would improve design quality. Skip when all design decisions are clear and the patterns are already established within the team.

**Action**: Use the Agent tool with `subagent_type: "aidlc-researcher"` to research design patterns, reference architectures, and technology recommendations relevant to the components being designed.

- **Inputs**: List of new components/services to design, known technology constraints, specific research questions.
- **Blocking**: Yes — wait for subagent completion before proceeding to Step 2.
- **On failure**: Surface research errors to user; do not silently skip.
- **Audit**: Append to `aidlc-docs/audit.md`:
  ```
  ## Subagent Invocation — aidlc-researcher
  **Timestamp**: [ISO 8601]
  **Stage**: Application Design
  **Purpose**: Design pattern and reference architecture research
  **Result**: [summary]
  ---
  ```

If condition is not met: log `"aidlc-researcher N/A — design patterns well-established"` in audit.md and proceed directly to Step 2.

---

### 2. Create Application Design Plan
- Generate plan with checkboxes [] for application design
- Focus on components, responsibilities, methods, business rules, and services
- Each step and sub-step should have a checkbox []

### 3. Include Mandatory Design Artifacts in Plan
- **ALWAYS** include these mandatory artifacts in the design plan:
  - [ ] Generate components.md with component definitions and high-level responsibilities
  - [ ] Generate component-methods.md with method signatures (business rules detailed later in Functional Design)
  - [ ] Generate services.md with service definitions and orchestration patterns
  - [ ] Generate component-dependency.md with dependency relationships and communication patterns
  - [ ] Validate design completeness and consistency

### 4. Generate Context-Appropriate Questions
**DIRECTIVE**: Analyze the requirements and stories to generate questions relevant to THIS specific application design. Use the categories below as guidance. Evaluate each category and, when in doubt about applicability, ask the question rather than skipping it — overconfidence leads to poor outcomes (see overconfidence-prevention.md).

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve design decisions
- **When in doubt, ask the question** - overconfidence leads to poor designs

**Question categories to evaluate** (consider ALL categories):
- **Component Identification** - Ask about component boundaries, organization, and grouping strategies
- **Component Methods** - Ask about method signatures, input/output expectations, and interface contracts (detailed business rules come later)
- **Service Layer Design** - Ask about service orchestration, boundaries, and coordination patterns
- **Component Dependencies** - Ask about communication patterns, dependency management, and coupling concerns
- **Design Patterns** - Ask about architectural style preferences, pattern choices, and design constraints

### 5. Store Application Design Plan
- Save as `aidlc-docs/inception/plans/application-design-plan.md`
- Include all [Answer]: tags for user input
- Ensure plan covers all design aspects

### 6. Request User Input
- Ask user to fill [Answer]: tags directly in the plan document
- Emphasize importance of design decisions
- Provide clear instructions on completing the [Answer]: tags

### 7. Collect Answers
- Wait for user to provide answers to all questions using [Answer]: tags in the document
- Do not proceed until ALL [Answer]: tags are completed
- Review the document to ensure no [Answer]: tags are left blank

### 8. ANALYZE ANSWERS (MANDATORY)
Before proceeding, you MUST carefully review all user answers for:
- **Vague or ambiguous responses**: "mix of", "somewhere between", "not sure", "depends"
- **Undefined criteria or terms**: References to concepts without clear definitions
- **Contradictory answers**: Responses that conflict with each other
- **Missing design details**: Answers that lack specific guidance
- **Answers that combine options**: Responses that merge different approaches without clear decision rules

### 9. MANDATORY Follow-up Questions
If the analysis in step 8 reveals ANY ambiguous answers, you MUST:
- Add specific follow-up questions to the plan document using [Answer]: tags
- DO NOT proceed to approval until all ambiguities are resolved
- Examples of required follow-ups:
  - "You mentioned 'mix of A and B' - what specific criteria should determine when to use A vs B?"
  - "You said 'somewhere between A and B' - can you define the exact middle ground approach?"
  - "You indicated 'not sure' - what additional information would help you decide?"
  - "You mentioned 'depends on complexity' - how do you define complexity levels?"

### 10. Generate Application Design Artifacts
- Execute the approved plan to generate design artifacts
- Create `aidlc-docs/inception/application-design/components.md` with:
  - Component name and purpose
  - Component responsibilities
  - Component interfaces
- Create `aidlc-docs/inception/application-design/component-methods.md` with:
  - Method signatures for each component
  - High-level purpose of each method
  - Input/output types
  - Note: Detailed business rules will be defined in Functional Design (per-unit, CONSTRUCTION phase)
- Create `aidlc-docs/inception/application-design/services.md` with:
  - Service definitions
  - Service responsibilities
  - Service interactions and orchestration
- Create `aidlc-docs/inception/application-design/component-dependency.md` with:
  - Dependency matrix showing relationships
  - Communication patterns between components
  - Data flow diagrams
- Create `aidlc-docs/inception/application-design/application-design.md` that consolidates the multiple design docs created above in a single doc.

### 11. Log Approval
- Log approval prompt with timestamp in `aidlc-docs/audit.md`
- Include complete approval prompt text
- Use ISO 8601 timestamp format

### 12. Present Completion Message

```markdown
# 🏗️ Application Design Complete

[AI-generated summary of application design artifacts created in bullet points]

> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the application design artifacts at: `aidlc-docs/inception/application-design/`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the application design if required
> [IF Units Generation is skipped:]
> 📝 **Add Units Generation** - Choose to include **Units Generation** stage (currently skipped)
> ✅ **Approve & Continue** - Approve design and proceed to **[Units Generation/CONSTRUCTION PHASE]**
```

### 13. Wait for Explicit Approval
- Do not proceed until the user explicitly approves the application design
- Approval must be clear and unambiguous
- If user requests changes, update the design and repeat the approval process

### 14. Record Approval Response
- Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- Include the exact user response text
- Mark the approval status clearly

### 15. Update Progress
- Mark Application Design stage complete in `aidlc-docs/aidlc-state.md`
- Update the "Current Status" section
- Prepare for transition to next stage
