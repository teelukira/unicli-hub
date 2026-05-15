# Build and Test

**Purpose**: Per-unit independent verification — build, test, TMF compliance, and (frontend only) web integration

## Prerequisites
- Code Generation must be complete for the unit currently in scope

## ADR Integrity Gate (MANDATORY when `ADR Governance: Enabled (Full)`)

In addition to the existing qa-tester / tmf-compliance-reviewer / web-integration-tester gates, this stage MUST verify ADR integrity for the unit just generated:

1. **Unit INDEX backlink**: `aidlc-docs/construction/{unit}/INDEX.md` MUST contain `**Relates-To-ADR**:` (line in first 30 lines). The PostToolUse hook `adr_backlink_check.py` enforces this, but the stage verifies as a safety net.
2. **Affected ADRs cited**: Any `Source-Evidence` in newly created/updated ADRs (from this stage's code generation) MUST reference real code paths/lines in the produced artifacts.
3. **Run verification**: Execute `bash scripts/verify-adr-integrity.sh` once before the build-and-test approval gate. BLOCKING 0건이어야 합니다.
4. **New decisions surfaced**: If qa-tester or tmf-compliance-reviewer findings reveal a new architectural decision (e.g., NC waive requested), STOP and invoke `adr-curator` before approval.

If `ADR Governance` extension is `Disabled` or `Manual`, this gate downgrades to advisory (non-blocking).

---

## Step 1: Analyze Testing Requirements

Analyze the unit to determine appropriate testing strategy:
- **Unit tests**: Already generated per unit during code generation
- **Integration tests**: Test interactions between units/services
- **Performance tests**: Load, stress, and scalability testing
- **End-to-end tests**: Complete user workflows
- **Contract tests**: API contract validation between services
- **Security tests**: Vulnerability scanning, penetration testing

---

## Step 1.5: Determine Unit Scope and Applicability

Before proceeding, evaluate the unit and set the verification checklist:

1. **Identify unit metadata**:
   - Unit name and type: `backend` / `frontend` / `mixed`
   - TMF standard unit? (See `extensions/tmf/compliance/tmf-compliance.md` Unit Applicability table)
   - Read `aidlc-docs/aidlc-state.md` → `## Extension Configuration` for enabled/disabled extensions

2. **Set verification gate checklist** (hold in memory for this stage):
   - `qa_tester` = **mandatory** (always)
   - `tmf_reviewer` = **mandatory** if TMF-standard unit AND TMF Compliance extension is Enabled; otherwise **N/A**
   - `web_integration_tester` = **mandatory** if unit type is `frontend` or `mixed`; otherwise **N/A**
     - **Skip permitted ONLY when**: pure backend/IaC unit (no `frontend/` files in scope), OR frontend unit scoped to design-system-only changes with zero feature integration (must be declared in Workflow Planning and approved by user)
     - Skipping E2E with rationale "백엔드 필요" / "backend dependency" is **NOT permitted** — the canonical Playwright `webServer` config auto-spawns required backends (bootJar → java -jar → Vite dev) without manual operator intervention
     - `E2E_FRONTEND_ONLY=true`로 실행하는 것도 **NOT permitted** — 네비게이션 전용 E2E는 API 통합 게이트를 충족하지 않음. 반드시 실 H2 백엔드와 함께 전체 E2E를 실행해야 함

3. **Log the checklist** to audit.md before executing Steps 2–7.
   - Append exact gate markers once verdicts are known:
     - `GATE-QA: PASS [unit={unit-name}]` or `GATE-QA: FAIL [unit={unit-name}]`
     - `GATE-TMF: PASS [unit={unit-name}]`, `GATE-TMF: FAIL [unit={unit-name}]`, or `GATE-TMF: N/A [unit={unit-name}]`
     - `GATE-WEB: PASS [unit={unit-name}]`, `GATE-WEB: CONDITIONAL PASS [unit={unit-name}]`, `GATE-WEB: FAIL [unit={unit-name}]`, or `GATE-WEB: N/A [unit={unit-name}]`

> **CRITICAL**: If an extension is Disabled in `aidlc-state.md`, skip its verification gate and log the skip in audit.md per `core-workflow.md` Extension Enforcement rules.

---

## Step 2: Generate Build Instructions

Create `aidlc-docs/construction/build-and-test/build-instructions.md`:

```markdown
# Build Instructions

## Prerequisites
- **Build Tool**: [Tool name and version]
- **Dependencies**: [List all required dependencies]
- **Environment Variables**: [List required env vars]
- **System Requirements**: [OS, memory, disk space]

## Build Steps

### 1. Install Dependencies
\`\`\`bash
[Command to install dependencies]
# Example: npm install, mvn dependency:resolve, pip install -r requirements.txt
\`\`\`

### 2. Configure Environment
\`\`\`bash
[Commands to set up environment]
# Example: export variables, configure credentials
\`\`\`

### 3. Build All Units
\`\`\`bash
[Command to build all units]
# Example: mvn clean install, npm run build, brazil-build
\`\`\`

### 4. Verify Build Success
- **Expected Output**: [Describe successful build output]
- **Build Artifacts**: [List generated artifacts and locations]
- **Common Warnings**: [Note any acceptable warnings]

## Troubleshooting

### Build Fails with Dependency Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]

### Build Fails with Compilation Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]
```

---

## Step 2.5: qa-tester Subagent (MANDATORY — BLOCKING)

**BLOCKING GATE**: This step MUST complete with PASS before proceeding to Step 3.

**CRITICAL**: Use the Agent tool with `subagent_type: "qa-tester"`. Do NOT act as the qa-tester role yourself.

1. Use the Agent tool with `subagent_type: "qa-tester"` for this unit:
   - **subagent_type**: `qa-tester`
   - **Inputs**: unit name, service directory path
   - The agent executes `./gradlew clean build`, runs all test categories, measures coverage
   - **Audit** — append to `aidlc-docs/audit.md` after completion:
     ```
     ## Subagent Invocation — qa-tester
     **Timestamp**: [ISO 8601]
     **Stage**: Build and Test
     **Unit**: [unit-name]
     **Purpose**: Independent build, test, and coverage verification
     **Result**: [PASS / FAIL]
     ---
     ```

2. **Expected outputs** (verify existence):
   - `aidlc-docs/construction/{unit}/build-and-test/build-report-{unit}.md`
   - `aidlc-docs/construction/{unit}/build-and-test/test-report-{unit}.md`

3. **On PASS**: Continue to Step 3.
   - Append exact audit marker: `GATE-QA: PASS [unit={unit-name}]`

4. **On FAIL**:
   - qa-tester produces `aidlc-docs/construction/{unit}/build-and-test/fix-request-{unit}.md`
   - Delegate fixes to the appropriate codegen agent (`codegen-backend`, `codegen-db`, etc.)
   - Re-invoke qa-tester after fixes (max **3 iterations**)
   - If still FAIL after 3 iterations: escalate to user with full diagnosis. **DO NOT mark stage complete.**
   - **"Continue to Next Stage" is BLOCKED until qa-tester verdict is PASS**
   - Append exact audit marker: `GATE-QA: FAIL [unit={unit-name}]`

---

## Step 3: Generate Unit Test Execution Instructions

Create `aidlc-docs/construction/build-and-test/unit-test-instructions.md`:

```markdown
# Unit Test Execution

## Run Unit Tests

### 1. Execute All Unit Tests
\`\`\`bash
[Command to run all unit tests]
# Example: mvn test, npm test, pytest tests/unit
\`\`\`

### 2. Review Test Results
- **Expected**: [X] tests pass, 0 failures
- **Test Coverage**: [Expected coverage percentage]
- **Test Report Location**: [Path to test reports]

### 3. Fix Failing Tests
If tests fail:
1. Review test output in [location]
2. Identify failing test cases
3. Fix code issues
4. Rerun tests until all pass
```

---

## Step 4: Generate Integration Test Instructions

Create `aidlc-docs/construction/build-and-test/integration-test-instructions.md`:

```markdown
# Integration Test Instructions

## Purpose
Test interactions between units/services to ensure they work together correctly.

## Test Scenarios

### Scenario 1: [Unit A] → [Unit B] Integration
- **Description**: [What is being tested]
- **Setup**: [Required test environment setup]
- **Test Steps**: [Step-by-step test execution]
- **Expected Results**: [What should happen]
- **Cleanup**: [How to clean up after test]

### Scenario 2: [Unit B] → [Unit C] Integration
[Similar structure]

## Setup Integration Test Environment

### 1. Start Required Services
\`\`\`bash
[Commands to start services]
# Example: docker-compose up, start test database
\`\`\`

### 2. Configure Service Endpoints
\`\`\`bash
[Commands to configure endpoints]
# Example: export API_URL=http://localhost:8080
\`\`\`

## Run Integration Tests

### 1. Execute Integration Test Suite
\`\`\`bash
[Command to run integration tests]
# Example: mvn integration-test, npm run test:integration
\`\`\`

### 2. Verify Service Interactions
- **Test Scenarios**: [List key integration test scenarios]
- **Expected Results**: [Describe expected outcomes]
- **Logs Location**: [Where to check logs]

### 3. Cleanup
\`\`\`bash
[Commands to clean up test environment]
# Example: docker-compose down, stop test services
\`\`\`
```

---

## Step 4.4: Refresh TMF Knowledge Oracle (CONDITIONAL)

**Condition**: Invoke ONLY if either condition holds:
- Any file under `docs/raw/` has mtime newer than the newest file under `docs/tmf-oracle/`.
- The unit introduces or changes a TMF API not previously covered in `docs/tmf-oracle/` (heuristic: grep `specs/tmf/{unit}/*.md` for TMFxxx references not present as `docs/tmf-oracle/tmfXXX-*.md`).

**Action**: Use the Agent tool with `subagent_type: "tmf-knowledge-ingest"` — pass the new/updated raw assets, expect refreshed `.md` chunks under `docs/tmf-oracle/`. This must complete before Step 4.5 (tmf-compliance-reviewer) so the reviewer reads the latest oracle.

**Audit** — append to `aidlc-docs/audit.md` after completion:
```
## Subagent Invocation — tmf-knowledge-ingest
**Timestamp**: [ISO 8601]
**Stage**: Build and Test
**Unit**: [unit-name]
**Purpose**: TMF Knowledge Oracle refresh before compliance review
**Result**: [summary]
---
```

If neither condition holds, mark "N/A — oracle current" in the build-test-report.md and proceed directly to Step 4.5.

---

## Step 4.5: tmf-compliance-reviewer Subagent (CONDITIONAL — BLOCKING if mandatory)

**Condition**: Execute ONLY if `tmf_reviewer = mandatory` (set in Step 1.5). Otherwise skip and log `"tmf-compliance-reviewer N/A — non-TMF-standard unit"` in audit.md.

**BLOCKING GATE**: If mandatory, this step MUST complete with PASS before proceeding to Step 5.

**CRITICAL**: Use the Agent tool with `subagent_type: "tmf-compliance-reviewer"`. Do NOT act as the reviewer role yourself.

1. Use the Agent tool with `subagent_type: "tmf-compliance-reviewer"` for this unit:
   - **subagent_type**: `tmf-compliance-reviewer`
   - **Inputs**: unit identifier (e.g., `u02`, `u03`)
   - **Audit** — append to `aidlc-docs/audit.md` after completion:
     ```
     ## Subagent Invocation — tmf-compliance-reviewer
     **Timestamp**: [ISO 8601]
     **Stage**: Build and Test
     **Unit**: [unit-name]
     **Purpose**: TMF-A~N compliance verification
     **Result**: [PASS / FAIL / N/A]
     ---
     ```

2. **Expected outputs** (verify existence):
   - `specs/tmf/{unit}/review-report.md` — verdict MUST be `PASS`
   - `specs/tmf/{unit}/compliance-evidence.md`
   - `specs/tmf/{unit}/component-mapping.md`

3. **On PASS** (0 BLOCKING findings): Continue to Step 5.
   - Append exact audit marker: `GATE-TMF: PASS [unit={unit-name}]`

4. **On FAIL**:
   - List all blocking findings under a **"TMF Compliance Findings"** section in `build-and-test-summary.md`
   - Fix findings → re-invoke reviewer until PASS
   - **"Continue to Next Stage" is BLOCKED until verdict is PASS**
   - Append exact audit marker: `GATE-TMF: FAIL [unit={unit-name}]`

5. **On N/A skip** (non-TMF-standard unit):
   - Log to `audit.md`: `TMF reviewer skipped — non-standard SKT extension ({unit} = {SKT-TMFC-XXX code})`
   - Mark `tmf_reviewer = N/A` in build-and-test-summary.md
   - Append exact audit marker: `GATE-TMF: N/A [unit={unit-name}]`

---

## Step 5: Generate Performance Test Instructions (If Applicable)

Create `aidlc-docs/construction/build-and-test/performance-test-instructions.md`:

```markdown
# Performance Test Instructions

## Purpose
Validate system performance under load to ensure it meets requirements.

## Performance Requirements
- **Response Time**: < [X]ms for [Y]% of requests
- **Throughput**: [X] requests/second
- **Concurrent Users**: Support [X] concurrent users
- **Error Rate**: < [X]%

## Setup Performance Test Environment

### 1. Prepare Test Environment
\`\`\`bash
[Commands to set up performance testing]
# Example: scale services, configure load balancers
\`\`\`

### 2. Configure Test Parameters
- **Test Duration**: [X] minutes
- **Ramp-up Time**: [X] seconds
- **Virtual Users**: [X] users

## Run Performance Tests

### 1. Execute Load Tests
\`\`\`bash
[Command to run load tests]
# Example: jmeter -n -t test.jmx, k6 run script.js
\`\`\`

### 2. Execute Stress Tests
\`\`\`bash
[Command to run stress tests]
# Example: gradually increase load until failure
\`\`\`

### 3. Analyze Performance Results
- **Response Time**: [Actual vs Expected]
- **Throughput**: [Actual vs Expected]
- **Error Rate**: [Actual vs Expected]
- **Bottlenecks**: [Identified bottlenecks]
- **Results Location**: [Path to performance reports]

## Performance Optimization

If performance doesn't meet requirements:
1. Identify bottlenecks from test results
2. Optimize code/queries/configurations
3. Rerun tests to validate improvements
```

---

## Step 5.5: web-integration-tester Subagent (CONDITIONAL — BLOCKING if mandatory)

**Condition**: Execute ONLY if `web_integration_tester = mandatory` (unit type is `frontend` or `mixed`, set in Step 1.5). Otherwise skip and log `"web-integration-tester N/A — backend-only unit"` in audit.md.

**CRITICAL**: Use the Agent tool with `subagent_type: "web-integration-tester"`. Do NOT act as the tester role yourself.

1. Use the Agent tool with `subagent_type: "web-integration-tester"` for this unit:
   - **subagent_type**: `web-integration-tester`
   - **Inputs**: unit name, frontend directory path, backend API base URL
   - **Audit** — append to `aidlc-docs/audit.md` after completion:
     ```
     ## Subagent Invocation — web-integration-tester
     **Timestamp**: [ISO 8601]
     **Stage**: Build and Test
     **Unit**: [unit-name]
     **Purpose**: API schema validation + Playwright E2E
     **Result**: [PASS / CONDITIONAL PASS / FAIL / N/A]
     ---
     ```

2. **The agent runs three phases**:
   - Phase 1: API schema validation (OpenAPI spec vs actual controller)
   - Phase 2: Local Playwright E2E — Playwright `webServer` auto-spawns backends (bootJar → java -jar h2 profile → Vite dev). Prerequisites: `frontend/.env.local` has `VITE_OIDC_ENABLED=false`, `playwright.config.ts` has `webServer` array, all API paths proxied in `vite.config.ts`, all backend services have `application-h2.yml`. **`E2E_FRONTEND_ONLY=true` 환경변수가 설정된 실행은 이 BLOCKING 게이트를 충족하지 않음 — 반드시 실 H2 백엔드와 함께 실행해야 함.**
   - Phase 3: dev-light environment E2E (if deployed)

3. **Expected output**: `aidlc-docs/construction/{unit}/build-and-test/web-integration-report-{unit}.md`

4. **Verdict**: PASS / CONDITIONAL PASS / FAIL
   - PASS or CONDITIONAL PASS: Continue to Step 6
   - FAIL: Fix and re-invoke. **"Continue to Next Stage" is BLOCKED until PASS or CONDITIONAL PASS**
   - Append exact audit marker on PASS: `GATE-WEB: PASS [unit={unit-name}]`
   - Append exact audit marker on CONDITIONAL PASS: `GATE-WEB: CONDITIONAL PASS [unit={unit-name}]`
   - Append exact audit marker on FAIL: `GATE-WEB: FAIL [unit={unit-name}]`
   - If Step 5.5 is skipped as N/A, append exact marker: `GATE-WEB: N/A [unit={unit-name}]`

---

## Step 6: Generate Additional Test Instructions (As Needed)

Based on project requirements, generate additional test instruction files:

### Contract Tests (For Microservices)
Create `aidlc-docs/construction/build-and-test/contract-test-instructions.md`:
- API contract validation between services
- Consumer-driven contract testing
- Schema validation

### Security Tests
Create `aidlc-docs/construction/build-and-test/security-test-instructions.md`:
- Vulnerability scanning
- Dependency security checks
- Authentication/authorization testing
- Input validation testing

### End-to-End Tests (Backend-Only or Optional)
Create `aidlc-docs/construction/build-and-test/e2e-test-instructions.md` for backend-only units where optional E2E coverage is desired:
- Complete user workflow testing (headless/API-level)
- Cross-service scenarios
- Note: Frontend units use `local-e2e-instructions.md` (Step 5.5) as the BLOCKING gate instead

---

## Step 7: Generate Test Summary

Create `aidlc-docs/construction/{unit}/build-and-test/build-and-test-summary.md`.

The following four sections are **MANDATORY** — do not omit any section even if the result is N/A:

```markdown
# Build and Test Summary — {unit}

## Build Status
- **Build Tool**: [Tool name]
- **Build Status**: [Success/Failed]
- **Build Artifacts**: [List artifacts]
- **Build Time**: [Duration]

## Test Execution Summary

### Unit Tests
- **Total Tests**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Coverage**: [X]%
- **Status**: [Pass/Fail]

### Integration Tests
- **Test Scenarios**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Status**: [Pass/Fail]

### Performance Tests
- **Response Time**: [Actual] (Target: [Expected])
- **Throughput**: [Actual] (Target: [Expected])
- **Error Rate**: [Actual] (Target: [Expected])
- **Status**: [Pass/Fail/N/A]

### Additional Tests
- **Contract Tests**: [Pass/Fail/N/A]
- **Security Tests**: [Pass/Fail/N/A]
- **E2E Tests**: [Pass/Fail/N/A]
- **Local-Server E2E (Frontend)**: [Pass/Fail/N/A — N/A 사유 필수: "pure backend unit" 또는 "design-system-only, Workflow Planning approved"]

## QA Verification (qa-tester)
- **Verdict**: [PASS/FAIL]
- **Build Report**: `aidlc-docs/construction/{unit}/build-and-test/build-report-{unit}.md`
- **Test Report**: `aidlc-docs/construction/{unit}/build-and-test/test-report-{unit}.md`
- **Fix Iterations**: [0–3]
- **Issues Resolved**: [List of issues fixed during QA iterations, or "none"]

## TMF Compliance Verification (tmf-compliance-reviewer)
- **Verdict**: [PASS/FAIL/N/A]
- **Reason if N/A**: [e.g., "non-standard SKT extension (SKT-TMFC-006)"]
- **Review Report**: `specs/tmf/{unit}/review-report.md` [or N/A]
- **Blocking Findings**: [List or "none"]

## Web Integration Verification (web-integration-tester)
- **Verdict**: [PASS/CONDITIONAL PASS/FAIL/N/A]
- **Reason if N/A**: [e.g., "backend-only unit"]
- **Integration Report**: `aidlc-docs/construction/{unit}/build-and-test/web-integration-report-{unit}.md` [or N/A]

## Overall Status
- **Build**: [Success/Failed]
- **All Tests**: [Pass/Fail]
- **QA Gate**: [PASS/FAIL]
- **TMF Gate**: [PASS/FAIL/N/A]
- **Web Integration Gate**: [PASS/CONDITIONAL PASS/FAIL/N/A]
- **Ready for Next Stage**: [Yes/No]

## Next Steps
[If all gates pass]: Ready to proceed to Operations phase
[If any gate fails]: Address failures and re-run
```

---

## Step 8: Update State Tracking

**Gate check before marking complete** — ALL of the following must hold:
- `qa-tester` verdict = PASS
- `tmf-compliance-reviewer` verdict = PASS or N/A
- `web-integration-tester` verdict = PASS, CONDITIONAL PASS, or N/A

Only when all gates pass:

Update `aidlc-docs/aidlc-state.md`:
- Mark `[x] Build and Test` for this unit with verdict summary
- Update unit status in Phase 1 table
- `aidlc-docs/audit.md` must already contain all of:
  - `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit-name}]`
  - `GATE-QA: PASS [unit={unit-name}]`
  - `GATE-TMF: PASS [unit={unit-name}]` or `GATE-TMF: N/A [unit={unit-name}]`
  - `GATE-WEB: PASS [unit={unit-name}]`, `GATE-WEB: CONDITIONAL PASS [unit={unit-name}]`, or `GATE-WEB: N/A [unit={unit-name}]`
- If any required marker is missing, stage advancement is BLOCKED until the marker or an explicit `GATE-WAIVER: approved-by-user [unit={unit-name}] reason=...` is recorded

---

## Step 9: Present Results to User

Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔨 Build and Test Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of build and test results
        - Format: "Build and test has completed with the following results:"
        - List build status and artifacts
        - List test results by category (unit, integration, performance, etc.)
        - List generated instruction files
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the build and test summary at: `aidlc-docs/construction/build-and-test/build-and-test-summary.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the build and test instructions based on your review
> ✅ **Approve & Continue** - Approve build and test results and proceed to **Operations**

---
```

If any blocking gate is still FAIL or required marker is missing, use a blocked variant instead:

```markdown
# 🔨 Build and Test Blocked

> **📋 <u>**REVIEW REQUIRED:**</u>**
> Blocking verification issues remain in `aidlc-docs/construction/build-and-test/build-and-test-summary.md`

> **🚫 <u>**NEXT STEP BLOCKED**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for fixes and re-run the failed gates

---
```

---

## Step 10: Log Interaction

**MANDATORY**: Log the stage completion in `aidlc-docs/audit.md`:

```markdown
## Build and Test Stage — {unit}
**Timestamp**: [ISO timestamp]
APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit-name}]
GATE-QA: PASS [unit={unit-name}]
GATE-TMF: PASS [unit={unit-name}] | GATE-TMF: N/A [unit={unit-name}]
GATE-WEB: PASS [unit={unit-name}] | GATE-WEB: CONDITIONAL PASS [unit={unit-name}] | GATE-WEB: N/A [unit={unit-name}]
**Build Status**: [Success/Failed]
**Test Status**: [Pass/Fail]
**QA Verification**: [PASS/FAIL] — build-report-{unit}.md, test-report-{unit}.md
**TMF Compliance**: [PASS/FAIL/N/A] — [reason if N/A, e.g. "SKT-TMFC-XXX non-standard extension"]
**Web Integration**: [PASS/CONDITIONAL PASS/FAIL/N/A] — [reason if N/A]
**Files Generated**:
- {unit}/build-and-test/build-instructions.md
- {unit}/build-and-test/unit-test-instructions.md
- {unit}/build-and-test/integration-test-instructions.md
- {unit}/build-and-test/build-and-test-summary.md
- {unit}/build-and-test/build-report-{unit}.md (qa-tester)
- {unit}/build-and-test/test-report-{unit}.md (qa-tester)
- specs/tmf/{unit}/review-report.md (tmf-compliance-reviewer, if applicable)

---
```
