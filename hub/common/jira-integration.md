# Jira Integration — AI-DLC Core Rules

**Scope**: 3단계 자동 연동 — Code Generation 진입 직전(티켓 생성 MANDATORY) → Code Generation Part 2(In Progress 전이) → Build and Test(Review 전이).

> **생성 시점 정책**: Requirements Analysis에서 미리 생성할 수 있으나, brownfield/SKIP 시나리오를 포함한
> 모든 경우에 **Code Generation Step 1a가 SSOT gate**다 — 티켓 없으면 여기서 반드시 생성.

**Description template SSOT**: `hub/templates/remotes/jira-issue.body.md` — `scripts/render-ai-dlc-remote-templates.py`로 `{변수}` 치환 후 Jira `description`에 사용. 변수 정의는 `variables.schema.yaml`, 사용법은 `templates/remotes/README.md`.
**Config**: `memory/jira-config.md` (defaults) + `memory/jira-config.local.md` (gitignored per-developer override).

---

## 0. Config 로드 순서

### Markdown (MCP `jira_create_issue` 필드)

```
1. hub/memory/jira-config.local.md  (있으면 우선)
2. hub/memory/jira-config.md        (기본값)
```

`jira-config.local.md`가 선언한 필드만 override — 나머지는 기본값 사용.

### 환경변수 (Jira `description` 템플릿 렌더만)

`scripts/render-ai-dlc-remote-templates.py --target jira` 실행 시, JSON values에 이어서:

```
1. <repo>/.env
2. <repo>/.env.local   (.env 대비 우선)
3. 프로세스 환경변수 (AI_DLC_JIRA_ASSIGNEE / AI_DLC_JIRA_REPORTER)
4. CLI --set KEY=VALUE (최우선)
```

- 파일 읽기 생략: `--no-env-files` (CI/테스트).
- 변수 이름·예시: 루트 `.env.example` 의 `AI_DLC_JIRA_*` 블록.

---

## 1. One-Time Discovery

**조건**: config의 `epic_key` 또는 `transition_id_inprogress`가 비어있을 때 자동 실행.

### 1-1. Epic 키 해석

```jql
project = NWAE AND issuetype = Epic AND summary ~ "TANGO-I" ORDER BY created DESC
```

- 결과 첫 번째 이슈의 key → `epic_key`에 저장.
- 결과 없음: 사용자에게 epic_key를 직접 입력하도록 요청 후 config에 저장.

### 1-2. Transition ID 해석 (In Progress)

- `jira_search` JQL `project = NWAE ORDER BY created DESC` → 최신 이슈 키 획득.
- `jira_get_transitions(issue_key)` 호출 → transition 목록에서 이름이 `진행` / `In Progress` / `Progress` 포함인 항목의 id 추출.
- → `transition_id_inprogress`에 저장.

### 1-3. Required Custom Fields (try-parse-retry)

**주의**: `jira_get_field_options`는 mandatory 필드를 식별하지 못함. 아래 전략 사용:

1. 최소 페이로드로 `jira_create_issue` 시도 (project_key, summary, issue_type="Story").
2. **400 응답** → 에러 메시지에서 missing field 이름 파싱.
3. 누락된 필드에 더미 값 추가 후 재시도.
4. 성공 시 → 해당 이슈 key를 audit.md에 `JIRA-DISCOVERY-TICKET: NWAE-XXX (삭제 필요)` 기록.
5. 필드 목록을 config의 `required_custom_fields`에 persist.
6. 연속 실패 시 → 전체 에러를 사용자에게 노출 후 진행 여부 확인.

### 1-4. 결과 저장

Discovery 완료 후 `memory/jira-config.md`의 해당 필드를 업데이트.
audit.md에 `JIRA-DISCOVERY: epic_key=..., transition_id=...` 기록.

---

## 2. Create Ticket (Code Generation Step 1a — SSOT gate)

**트리거**: Code Generation Step 1a에서 `**Jira Ticket**`이 없을 때 호출.
Requirements Analysis에서 미리 생성됐다면 이 섹션은 skip (중복 방지 조건은 동일).

**중복 방지**: `aidlc-state.md`에 이미 실제 프로젝트 키(`**Jira Ticket**`)가 있으면 새 이슈를 만들지 말 것. Code Generation에서 키가 비어 있을 때만 동일 절차(미리보기 + `APPROVAL-JIRA-CREATE`)로 보강 생성.

### 2-1. 사용자 승인 게이트 (`common/approval-gates.md` 준수)

생성할 Jira 이슈 JSON을 사용자에게 preview로 보여주고 명시적 승인 요청.

```markdown
**[Jira 티켓 생성 미리보기]**
- 프로젝트: NWAE
- 요약(summary): [{unit-id}] {간결한 기능 제목} — 기능·개선점 중심, ~50자 권장
- 유형: 작업(Task)
- 담당자: 류근호
- 보고자: 류근호 (additional_fields)
- 설명(description): (아래 템플릿 렌더 결과)

생성 승인하시겠습니까? (Y/N)
```

승인 후 `aidlc-docs/audit.md`에 아래 marker를 정확히 기록:

```text
APPROVAL-JIRA-CREATE: granted [unit=u17]
```

### 2-2. API 호출

```
jira_create_issue(
  project_key  = config.project_key,           # "NWAE"
  summary      = "[{unit-id}] {간결한 기능 제목}",
  issue_type   = config.issue_type,            # "작업(Task)"
  assignee     = config.assignee,              # top-level 파라미터
  description  = <`scripts/render-ai-dlc-remote-templates.py`로 `hub/templates/remotes/jira-issue.body.md` 렌더 결과>,
  additional_fields = JSON({
    "reporter":    {"name": config.reporter},  # ← top-level 없음, 반드시 additional_fields
    ...config.required_custom_fields
  })
)
```

**복수 work item**: 요구사항에서 work item이 명시적으로 분리된 경우(예: W-1/W-2/W-3) 각 work item당 1개 티켓 생성. 각 티켓 summary는 해당 work item의 간결한 기능명만 사용 — 전체 unit-title 나열 금지. 단일 unit에 1개 work item이면 1개 티켓.

**MR 본문 포함**: 생성된 모든 ticket key를 `NWAE-XXX` 형식으로 space-separated로 MR **본문**(`{jira_keys}`)에 기록. MR **제목**에는 키를 넣지 않음 — 제목은 기능 요약만.

**`epic_link` vs `epicKey`**: SKT Jira DC (서버형)는 `additional_fields`에 `"epic_link"` (customfield_10014 alias) 또는 `"epicKey"`. Discovery 시 확인된 형태 사용.

### 2-3. 결과 처리

| 결과 | 처리 |
|------|------|
| 성공 | Story key를 `aidlc-state.md` 해당 unit 행 `jira_ticket`에 기록. audit.md에 `JIRA-CREATED: NWAE-### [unit=u17]` 기록. |
| 400 (field 오류) | 에러 파싱 → 1회 재시도 (Discovery 1-3과 동일 전략). 재시도도 실패 시 → Failure 처리. |
| 기타 실패 | **Failure 처리** (아래 §4). 워크플로우는 계속. |

### 2-4. Blocking semantics

- **Cursor `beforeMCPExecution` / `preToolUse` fail-closed 계약**: `failClosed: true` 훅은 **허용 시에도** stdout에 JSON 한 줄을 출력해야 한다. `exit 0`인데 stdout이 비어 있으면 Cursor가 “hook returned no output”으로 **도구 전체를 차단**한다. Jira/GitLab 가드뿐 아니라 `code_location_guard` / `generated_file_guard` / `workflow_transition_guard` 등 동일 패턴 훅은 `{"permission":"allow"}`를 출력한 뒤 `0`을 반환한다(참고: `shell_sensitive_file_guard.py`의 `allow()`).
- Jira Story 생성은 원격 시스템 변경이므로 `APPROVAL-JIRA-CREATE: granted [unit=...]` marker 없이 실행하면 안 된다.
- `aidlc-state.md`에서 Code Generation stage를 완료 처리하기 전에, 다음 둘 중 하나가 반드시 존재해야 한다:
  - 실제 `JIRA-CREATED: NWAE-### [unit=...]` marker + `**Jira Ticket**: NWAE-###`
  - `JIRA-WAIVER: approved-by-user [unit=...] reason=...`
- `TODO-NWAE-*` placeholder는 recovery indicator일 뿐이며, stage advancement를 만족시키지 않는다.
- **`Jira Ticket`: N/A + GitLab MR 금지**: Active Workstream에 `**Jira Ticket**: N/A`(또는 비어 있음)로 두고 GitLab MR을 열려 하면 `gitlab_mr_gate_guard`에 걸린다(동일 unit에 `JIRA-WAIVER` 없을 때). 스펙·문서-only·cosmetic 유닛이라도 **MR을 열 계획이면** Requirements Analysis 직후 `§2`로 Task 1건을 만들고 `**Jira Ticket**: NWAE-###`를 SSOT에 기록한다. 정말 티켓이 불필요하면 MR 전에 사용자 승인 하에 `JIRA-WAIVER: approved-by-user [unit=...] reason=...`를 `audit.md`에 남긴다.
- **Agent 자기 점검**: Construction(Code Generation)에 들어가기 전에 Active Workstream의 `**Jira Ticket**` 줄이 실제 `NWAE-###`인지 확인한다. `N/A`이면 티켓 생성(또는 waiver)부터 처리한다.

---

## 3. Transition to In Progress (Code Generation Part 2 시작 시)

```
1. aidlc-state.md에서 현재 unit의 jira_ticket 값 읽기.
2. 값이 "TODO-NWAE-..." 패턴이면:
   - audit.md에 "JIRA-RECONCILE-NEEDED: unit=..., placeholder=..." 기록.
   - skip (비blocking).
3. 값이 실제 NWAE-### 이면:
   - jira_get_transitions(issue_key) 호출.
   - 이미 "In Progress" 상태이면 skip.
   - jira_transition_issue(issue_key, transition_id_inprogress) 호출.
4. 성공 시 audit.md에 `JIRA-INPROGRESS: NWAE-### [unit=u17]` 기록.
5. 실패 시 Failure 처리 또는 명시적 `JIRA-WAIVER` 없이는 다음 stage/state advance 금지.
```

---

## 3a. Transition to Review (Build and Test 승인 직후)

Build and Test 완료 = 코드 완성 + QA 통과. 티켓을 검토(Review) 상태로 전이해 human reviewer에게 넘긴다.
MR merge 후 최종 Done/Closed는 개발자가 처리한다.

```
1. aidlc-state.md에서 현재 unit의 모든 jira_ticket 값 읽기.
2. 각 ticket에 대해:
   - jira_get_transitions(issue_key) 호출.
   - 이미 검토(Review)/완료(Done) 상태이면 skip.
   - jira_transition_issue(issue_key, transition_id_review) 호출.
     (config: transition_id_review = "111"  ← "Resolve" → 검토(Review))
3. 성공 시 audit.md에 `JIRA-REVIEW: NWAE-### [unit=Uxx]` 기록.
4. 실패 시 Failure 처리 (§4). 워크플로우는 계속.
```

---

## 4. Failure Handling

MCP 실패 또는 Jira API 에러 시:

```
1. placeholder 생성: TODO-NWAE-{unix-timestamp} (예: TODO-NWAE-1746959400)
2. aidlc-state.md 해당 unit jira_ticket 컬럼에 placeholder 기록.
3. audit.md에 아래 형식으로 기록:

   ## Jira Integration — FAILED
   **Timestamp**: [ISO 8601]
   **Unit**: [unit-name]
   **Operation**: CREATE | TRANSITION
   **Error**: [error message]
   **Placeholder**: TODO-NWAE-1746959400
   **Action Required**: manual reconcile — create/transition NWAE ticket and update aidlc-state.md
   ---

4. placeholder 기록 자체는 허용되지만, `JIRA-WAIVER: approved-by-user [unit=...] reason=...`가 없으면 stage advancement는 차단된다.
```

---

## 5. `aidlc-state.md` jira_ticket 컬럼

각 Construction unit 섹션에 `jira_ticket` 필드 추가:

```markdown
## AI-DLC [unit-name] Workstream (Uxx — ...)
- **Status**: 작업중
- **Jira Ticket**: NWAE-456   ← 이 필드 (없으면 추가)
- **Started**: 2026-05-11T04:30Z
```

`prepare-commit-msg` 훅은 이 필드의 값을 읽어 커밋 메시지에 자동 삽입.

---

## 6. Render Contract

### 입력 (9개 변수)

JSON 파일 — 변수 목록은 `variables.schema.yaml` 참조:

```json
{
  "jira_keys": "NWAE-123 NWAE-124",
  "unit_name": "u25",
  "unit_title": "...",
  "requirements_path": "aidlc-docs/inception/requirements/u25-requirements.md",
  "execution_plan_path": "aidlc-docs/inception/plans/u25-execution-plan.md",
  "code_gen_plan_path": "aidlc-docs/construction/plans/u25-code-generation-plan.md",
  "approved_at": "2026-05-13T12:00:00Z",
  "reporter": "류근호",
  "assignee": "류근호"
}
```

`--target jira` 렌더 시 §0의 `AI_DLC_JIRA_ASSIGNEE` / `AI_DLC_JIRA_REPORTER`(파일·프로세스)가 위 JSON의 `assignee` / `reporter`를 비어 있지 않으면 덮어씁니다.

### 명령

```bash
# Jira description → stdout (jira_create_issue description 파라미터)
python3 scripts/render-ai-dlc-remote-templates.py \
  --target jira \
  --values-file /tmp/vars.json

# GitLab MR description body → stdout (gitlab_create_merge_request description에 append)
python3 scripts/render-ai-dlc-remote-templates.py \
  --target gitlab-body \
  --values-file /tmp/vars.json
```

### 호출자

| 호출자 | Target | 시점 |
|--------|--------|------|
| `aidlc-requirements-analysis` Step 10 | `--target jira` | 요구사항 승인 직후 |
| `aidlc-build-and-test` Step 11 | `--target gitlab-body` | MR 생성 시 description body |

### fill-in 템플릿 동기화

`.gitlab/merge_request_templates/default.md`는 **렌더 산출물이 아닌 fill-in 템플릿** (GitLab UI에서 개발자가 직접 채움).
소스: `hub/templates/remotes/gitlab-mr.default.md` — byte-equal 동기화.
drift 감지: `pre-commit` 훅 `aidlc-remote-templates-check` → `python3 scripts/render-ai-dlc-remote-templates.py --check`.
