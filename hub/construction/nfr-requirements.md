# NFR Requirements

## Prerequisites
- Functional Design must be complete for the unit
- Unit functional design artifacts must be available
- Execution plan must indicate NFR Requirements stage should execute

## Overview
Determine non-functional requirements for the unit and make tech stack choices.

## Steps to Execute

### Step 1: Analyze Functional Design
- Read functional design artifacts from `aidlc-docs/construction/{unit-name}/functional-design/`
- Understand business logic complexity and requirements

### Step 1.5: aidlc-researcher NFR Benchmarks (CONDITIONAL)

**Condition**: Invoke when NFR requirements include performance SLAs, scalability targets, or industry-specific compliance requirements where current benchmarks and standards would inform better decisions. Skip when all performance/security targets are already specified in the requirements document.

**Action**: Use the Agent tool with `subagent_type: "aidlc-researcher"` to research current industry benchmarks, NFR standards, and technology-specific performance characteristics.

- **Inputs**: Unit functional design summary, list of NFR areas requiring research (e.g., "p99 latency for TMF639 API", "EKS node sizing for 1000 RPS", "OWASP ASVS level for public API").
- **Blocking**: Yes — wait for subagent completion before proceeding to Step 2.
- **On failure**: Surface research errors to user; do not silently skip.
- **Audit**: Append to `aidlc-docs/audit.md`:
  ```
  ## Subagent Invocation — aidlc-researcher
  **Timestamp**: [ISO 8601]
  **Stage**: NFR Requirements
  **Unit**: [unit-name]
  **Purpose**: NFR benchmark and standards research
  **Result**: [summary]
  ---
  ```

If condition is not met: log `"aidlc-researcher N/A — NFR targets already specified in requirements"` in audit.md and proceed directly to Step 2.

---

### Step 2: Create NFR Requirements Plan
- Generate plan with checkboxes [] for NFR assessment
- Focus on scalability, performance, availability, security
- Each step should have a checkbox []

### Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the functional design to identify ALL areas where NFR clarification would improve system quality and architecture decisions. Be proactive in asking questions to ensure comprehensive NFR coverage.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect system quality. It's better to ask too many questions than to make incorrect NFR assumptions.

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve NFR and tech stack decisions
- **When in doubt, ask the question** - overconfidence leads to poor system quality

**Question categories to evaluate** (consider ALL categories):
- **Scalability Requirements** - Ask about expected load, growth patterns, scaling triggers, and capacity planning
- **Performance Requirements** - Ask about response times, throughput, latency, and performance benchmarks
- **Availability Requirements** - Ask about uptime expectations, disaster recovery, failover, and business continuity
- **Security Requirements** - Ask about data protection, compliance, authentication, authorization, and threat models
- **Tech Stack Selection** - Ask about technology preferences, constraints, existing systems, and integration requirements
- **Reliability Requirements** - Ask about error handling, fault tolerance, monitoring, and alerting needs
- **Maintainability Requirements** - Ask about code quality, documentation, testing, and operational requirements
- **Usability Requirements** - Ask about user experience, accessibility, and interface requirements

### Step 4: Store Plan
- Save as `aidlc-docs/construction/plans/{unit-name}-nfr-requirements-plan.md`
- Include all [Answer]: tags for user input

### Step 5: Collect and Analyze Answers
- Wait for user to complete all [Answer]: tags
- **MANDATORY**: Carefully review ALL responses for vague or ambiguous answers
- **CRITICAL**: Add follow-up questions for ANY unclear responses - do not proceed with ambiguity
- Look for responses like "depends", "maybe", "not sure", "mix of", "somewhere between", "standard", "typical"
- Create clarification questions file if ANY ambiguities are detected
- **Do not proceed until ALL ambiguities are resolved**

### Step 6: Generate NFR Requirements Artifacts
- Create `aidlc-docs/construction/{unit-name}/nfr-requirements/nfr-requirements.md`
- Create `aidlc-docs/construction/{unit-name}/nfr-requirements/tech-stack-decisions.md`

### Step 7: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 📊 NFR Requirements Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of NFR requirements
        - Format: "NFR requirements assessment has identified [description]:"
        - List key scalability, performance, availability requirements (bullet points)
        - List security and compliance requirements identified
        - Mention tech stack decisions and rationale
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the NFR requirements at: `aidlc-docs/construction/[unit-name]/nfr-requirements/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the NFR requirements based on your review
> ✅ **Continue to Next Stage** - Approve NFR requirements and proceed to **[next-stage-name]**

---
```

### Step 8: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the NFR requirements
- Approval must be clear and unambiguous
- If user requests changes, update the requirements and repeat the approval process

### Step 9: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark NFR Requirements stage complete in aidlc-state.md
