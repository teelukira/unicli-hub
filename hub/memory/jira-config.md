---
name: jira-config
description: Default Jira project/epic/assignee for workflow auto-ticketing. Fill in your project values.
type: memory
---

# Jira Integration Config

## Defaults

```yaml
project_key: "{TBD}"               # e.g. NWAE
epic_name: "{TBD}"                  # e.g. "[MyProject] Epic Name"
epic_key: "{TBD}"                   # e.g. PROJ-123
epic_field: "customfield_10001"     # Jira Server Epic Link field ID
issue_type: "{TBD}"                 # e.g. "Task" or "Story"
reporter: "{TBD}"                   # Display name
assignee: "{TBD}"                   # Display name
assignee_username: "{TBD}"          # Login username (used for MCP jira_create_issue)
transition_id_inprogress: "{TBD}"   # "Start Progress" transition ID
transition_id_done: "{TBD}"         # "Resolve" / "Done" transition ID
required_custom_fields: {}
```

## MCP 사용 시 주의사항

**담당자 (Assignee)**
- `jira_create_issue` 의 `assignee` 파라미터: **표시 이름 아닌 username** 전달
- 표시 이름은 Jira Server 에서 조용히 실패하고 Unassigned 로 생성될 수 있음

**에픽 (Epic Link)**
- `jira_create_issue` 의 `additional_fields` 로 전달: `{"customfield_10001": "PROJ-123"}`
- Jira Server/DC 는 `epicKey` 단축 파라미터 미지원

## Developer Overrides

개발자별 설정 변경은 **`memory/jira-config.local.md`** 파일 생성 (gitignored).
예시는 `memory/jira-config.local.md.example` 참조.

우선순위: `jira-config.local.md` > 이 파일 (기본값).
