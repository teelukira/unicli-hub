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

**Context compression 또는 세션 재개 시, Code Generation 단계 이후라면 반드시 Jira 상태를 확인할 것.**

### 확인 절차 (Construction 재개 시)

1. `aidlc-state.md`에서 현재 unit의 `Jira Ticket` 필드 확인.
2. **필드 없음 또는 `TODO-NWAE-*` 패턴**:
   - `aidlc-docs/audit.md`에서 `APPROVAL-JIRA-CREATE: granted [unit=...]` 또는 `JIRA-WAIVER: approved-by-user [unit=...]` 확인
   - 승인 marker가 있으면 Jira 생성/전이 수행
   - 승인 marker가 없으면 **자동 생성 금지**. `JIRA-RECONCILE-BLOCKED [unit=...]`를 audit.md에 기록하고 사용자 승인 요청
3. **실제 NWAE-### 값**: 현재 상태가 `진행중(In Progress)`인지 확인 → 아니면 전이.

### 실수 방지 체크리스트

Code Generation Part 1 (계획) 승인 후 반드시:
- [ ] `aidlc-state.md` 해당 unit에 `- **Jira Ticket**: NWAE-###` 행 추가
- [ ] `audit.md`에 `APPROVAL-JIRA-CREATE: granted [unit=...]` 기록
- [ ] `audit.md`에 `JIRA-CREATED: NWAE-### [unit=...]` 기록

Code Generation Part 2 (실행) 시작 전:
- [ ] `jira_transition_issue` 호출로 In Progress 전이
- [ ] `audit.md`에 `JIRA-INPROGRESS: NWAE-### [unit=...]` 기록

### 세션 재개 후 자동 진단

세션 재개 시 aidlc-state.md를 읽어 Construction 단계가 Code Generation 이후인데 Jira Ticket 필드가 없으면:
- prior approval marker가 있을 때만 Jira 생성 절차를 즉시 실행
- prior approval marker가 없으면 자동 생성하지 말고 `JIRA-RECONCILE-BLOCKED [unit=...]`를 남긴 뒤 사용자에게 승인 요청
- 완료 후 "Jira NWAE-### 생성 및 In Progress 전이 완료" 한 줄 보고

## Error Handling
If artifacts are missing or corrupted during session resumption, see [error-handling.md](error-handling.md) for guidance on recovery procedures.
