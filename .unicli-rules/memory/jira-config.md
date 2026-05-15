---
name: jira-config
description: Default Jira project/epic/assignee for AI-DLC workflow auto-ticketing (project=NWAE, epic=[nOSS]TANGO-I, default developer=류근호)
type: project
---

# Jira Integration Config

## Defaults

```yaml
project_key: NWAE
epic_name: "[nOSS]TANGO-I"
epic_key: "NWAE-326"              # Epic Link 연결 키 (.env.example AI_DLC_JIRA_EPIC_KEY)
epic_field: "customfield_10001"   # Jira Server Epic Link 필드 ID (jira_create_issue additional_fields로 전달)
issue_type: "작업(Task)"           # Discovery 2026-05-13 확인 (Story 아님)
reporter: 류근호
assignee: 류근호
assignee_username: "1111207"      # MCP jira_create_issue assignee 인자 — 표시 이름(류근호) 아닌 username 사용
transition_id_inprogress: "21"    # "Start Progress"  To Do → 진행중(In Progress)
transition_id_done: "111"         # "Resolve"  In Progress → 검토(Review) [완료 카테고리]
required_custom_fields: {}         # Auto-populated by try-parse-retry Discovery
```

## MCP 도구 사용 시 주의사항

**담당자(Assignee)**
- `jira_create_issue`의 `assignee` 파라미터: **표시 이름("류근호") 아닌 username("1111207")** 전달
- 표시 이름은 이 Jira Server 인스턴스에서 조용히 실패하고 Unassigned로 생성됨 (2026-05-14 확인)

**에픽(Epic Link)**
- `jira_create_issue`의 `additional_fields`로 전달: `{"customfield_10001": "NWAE-326"}`
- Jira Server/DC는 `epicKey` 단축 파라미터 미지원 — 반드시 `customfield_10001` 사용
- 에픽 키: `NWAE-326` (.env.example `AI_DLC_JIRA_EPIC_KEY` 기준)

## Developer Overrides

개발자별 설정 변경은 **`memory/jira-config.local.md`** 파일 생성 (gitignored).
예시는 `memory/jira-config.local.md.example` 참조.

우선순위: `jira-config.local.md` > 이 파일 (기본값).

**Why:** 보고자/작업자를 개발자마다 다르게 설정하되 프로젝트 공통 설정(project_key, epic)은 공유.
**How to apply:** Jira 티켓 생성 전 local override를 먼저 로드하고, 없는 필드는 이 파일에서 채움.

### 템플릿 렌더용 환경변수 (선택)

Jira 이슈 **본문(description)** 렌더 시 담당/보고를 JSON 대신 루트 `.env` / `.env.local`에서 쓰려면 `AI_DLC_JIRA_ASSIGNEE`, `AI_DLC_JIRA_REPORTER`를 설정하세요. (`scripts/render-ai-dlc-remote-templates.py --target jira`, 루트 `.env.example` 참고.) MCP로 이슈를 만들 때의 `assignee` / `reporter` 인자는 위 YAML 기본값·local md가 우선입니다.

