# Session Continuity Templates

## Welcome Back Prompt Template
When a user returns to continue work on an existing AI-DLC project, present this prompt:

```markdown
**Welcome back! I can see you have an existing AI-DLC project in progress.**

Based on your aidlc-state.md, here's your current status:
- **Project**: [project-name]
- **Current Phase**: [INCEPTION/CONSTRUCTION/OPERATIONS]
- **Current Stage**: [Stage Name]
- **Last Completed**: [Last completed step]
- **Next Step**: [Next step to work on]

**What would you like to work on today?**

A) Continue where you left off ([Next step description])
B) Review a previous stage ([Show available stages])

[Answer]:
```

## MANDATORY: Session Continuity Instructions
1. **Always read aidlc-state.md first** when detecting existing project
2. **Parse current status** from the workflow file to populate the prompt
3. **MANDATORY: Load Previous Stage Artifacts** - Before resuming any stage, automatically read all relevant artifacts from previous stages:
   - **Reverse Engineering**: Read architecture.md, code-structure.md, api-documentation.md
   - **Requirements Analysis**: Read requirements.md, requirement-verification-questions.md
   - **User Stories**: Read stories.md, personas.md, story-generation-plan.md
   - **Application Design**: Read application-design artifacts (components.md, component-methods.md, services.md)
   - **Design (Units)**: Read unit-of-work.md, unit-of-work-dependency.md, unit-of-work-story-map.md
   - **Per-Unit Design**: Read functional-design.md, nfr-requirements.md, nfr-design.md, infrastructure-design.md
   - **Code Stages**: Read all code files, plans, AND all previous artifacts
4. **Smart Context Loading by Stage**:
   - **Early Stages (Workspace Detection, Reverse Engineering)**: Load workspace analysis
   - **Requirements/Stories**: Load reverse engineering + requirements artifacts
   - **Design Stages**: Load requirements + stories + architecture + design artifacts
   - **Code Stages**: Load ALL artifacts + existing code files
5. **Adapt options** based on architectural choice and current phase
6. **Show specific next steps** rather than generic descriptions
7. **Log the continuity prompt** in audit.md with timestamp
8. **Context Summary**: After loading artifacts, provide brief summary of what was loaded for user awareness
9. **Asking questions**: ALWAYS ask clarification or user feedback questions by placing them in .md files. DO NOT place the multiple-choice questions in-line in the chat session.

## MANDATORY: Jira Reconciliation on Resume

**Context compression or session resume: if at Code Generation stage or later, always check Jira status.**

### Verification Steps (Construction Resume)

1. Check current unit's `Jira Ticket` field in `aidlc-state.md`.
2. **Field absent or `TODO-NWAE-*` pattern**: Jira ticket not created -> create immediately and transition to In Progress.
3. **Actual NWAE-### value**: Verify current status is `In Progress` -> if not, transition.

### Error Prevention Checklist

After Code Generation Part 1 (plan) approval, MUST:
- [ ] Add `- **Jira Ticket**: NWAE-###` row to the unit in `aidlc-state.md`
- [ ] Write `JIRA-CREATED: NWAE-###` to `audit.md`

Before starting Code Generation Part 2 (execution):
- [ ] Call `jira_transition_issue` to transition to In Progress
- [ ] Write `JIRA-INPROGRESS: NWAE-###` to `audit.md`

### Auto-Diagnosis on Session Resume

On session resume, read aidlc-state.md. If Construction stage is Code Generation or later but Jira Ticket field is absent:
- Do NOT ask the user separately — immediately execute Jira creation procedure
- After completion, report: "Jira NWAE-### created and transitioned to In Progress" in one line

## Error Handling
If artifacts are missing or corrupted during session resumption, see `hub/common/error-handling.md` for guidance on recovery procedures.
