# 원격 템플릿 (지라 + GitLab)

저장소 밖에서 쓰는 마크다운 본문의 SSOT(지라 이슈 `description`, GitLab MR 설명).

| 파일 | 역할 |
|------|------|
| `jira-issue.body.md` | 지라 `description` — `{중괄호}` 플레이스홀더, 실행 시 렌더 |
| `gitlab-mr.body.md` | GitLab MR 설명 본문 — `{중괄호}` 플레이스홀더, 실행 시 렌더 |
| `gitlab-mr.default.md` | MR 작성용 채움 템플릿. `.gitlab/merge_request_templates/default.md`와 바이트 동일 동기화 |
| `variables.schema.yaml` | 변수 정의(`type`/`required`/`pattern`) — 렌더러가 검증 |
| `fixtures/check-values.json` | 스모크 테스트·드리프트 검출용 값 |

## 지라 담당자·보고자(선택)

렌더 `--target jira` 시 저장소 루트 `.env` 다음 `.env.local`에서 `AI_DLC_JIRA_ASSIGNEE`, `AI_DLC_JIRA_REPORTER`를 읽는다(비어 있지 않으면 JSON 값 파일을 덮어씀). 프로세스 환경 변수가 둘 다 덮어쓴다. CI에서는 `.env`/`.env.local`을 읽지 않으려면 `--no-env-files` 사용. 루트 `.env.example` 참고.

## 렌더 실행 예

```bash
# 지라 description → stdout
python3 scripts/render-ai-dlc-remote-templates.py \
  --target jira \
  --values-file /tmp/vars.json

# GitLab MR 본문 → stdout
python3 scripts/render-ai-dlc-remote-templates.py \
  --target gitlab-body \
  --values-file /tmp/vars.json

# 채움 템플릿 드리프트 검사(pre-commit)
python3 scripts/render-ai-dlc-remote-templates.py --check
```

## 스키마

`variables.schema.yaml`에 변수 9개가 정의되어 있다. 각 항목은 다음을 지원한다:

```yaml
my_var:
  description: 사람이 읽기 쉬운 설명
  type: string        # 현재는 항상 string
  required: true      # 값 누락 시 렌더 전 SystemExit
  pattern: '^regex$'  # 값 불일치 시 렌더 전 SystemExit
```

렌더러는 대상 템플릿에 등장하는 변수만 검증하므로, 템플릿이 참조하지 않는 선택 변수는 무시된다.

## 테스트

```bash
python3 scripts/tests/test_render_validation.py
```

에이전트는 지라/MR 본문에 `--target` 플래그를 사용해야 한다(`--template` 아님). 사람용 안내: `docs/templates/jira-issue.md`.
