# Git Worktree Conventions

## Directory Structure

모든 worktree는 다음 경로에 위치:

```
{repo-root}/git-worktrees/{type}/{branch-name}/
```

브랜치 명도 동일 패턴: `{type}/{branch-name}`

실제 구조 (현 프로젝트):
```
/Users/1111207/Documents/orion/
├── (main worktree — 기본 체크아웃)
└── git-worktrees/
    ├── feature/     # 신규 기능·유닛
    ├── fix/         # 버그픽스·교정
    └── chore/       # 문서·리팩토링·도구
```

---

## Branch Types

| Type | 사용 상황 | 명명 예시 |
|------|---------|---------|
| `feature/` | 신규 AI-DLC 유닛, 새 기능 구현 | `feature/u17-search-seeding` |
| `fix/` | 버그 수정, UX 교정 | `fix/u17-resource-ui`, `fix/u17-ux` |
| `chore/` | 문서 정리, 리팩토링, 비코드 작업 | `chore/docs-ssot` |

**규칙**: 코드 변경(feature/fix)과 문서/인프라 변경(chore)은 브랜치를 분리.

**명명 규칙**: 패턴 `{type}/{unit-id}-{1~3단어 kebab}`. `ai-dlc-` 등 중복 prefix 금지. 유닛 없는 작업은 unit-id 생략.

---

## Worktree 생성 명령

```bash
# 항상 main 기반으로 분기
git -C /Users/1111207/Documents/orion worktree add -b {type}/{name} \
  /Users/1111207/Documents/orion/git-worktrees/{type}/{name} main

# 예시
git -C /Users/1111207/Documents/orion worktree add -b chore/aidlc-docs-ssot-consolidation \
  /Users/1111207/Documents/orion/git-worktrees/chore/aidlc-docs-ssot-consolidation main
```

생성 직후 상태 확인:
```bash
git -C /Users/1111207/Documents/orion worktree list
```

---

## 핵심 규칙

1. **항상 main 기반** — 특별한 이유 없이 다른 브랜치에서 분기하지 않는다.
2. **main에는 커밋하지 않음** — 기능·수정 커밋은 `{type}/{name}` 브랜치(또는 해당 worktree)에서만 한다. `main`은 분기·동기화(`pull`)용.
3. **main worktree는 그대로** — main의 uncommitted 변경은 main 체크아웃에 남음. 신규 worktree는 마지막 커밋(HEAD) 기준 clean state로 시작.
4. **한 worktree = 한 관심사** — feature + fix 혼합 금지.
5. **worktree 내 작업** — `cd git-worktrees/{type}/{name}` 후 작업. git 명령은 해당 디렉토리에서 실행.

---

## main 반영 절차 (SSOT: GitLab MR)

**`main`에 코드를 합치는 유일한 경로는 GitLab에서 Merge Request를 머지하는 것이다.** 로컬 `main`에서 `git merge feature` 후 `push origin main` 하지 않는다.

상세·트러블슈팅: [`docs/conventions/gitlab-mr-workflow.md`](../../docs/conventions/gitlab-mr-workflow.md)

```bash
# 0) 시작 전 — main 최신화 (커밋 없음)
cd /Users/1111207/Documents/orion
git checkout main && git pull origin main

# 1) worktree/브랜치에서 작업·커밋 (위 §Worktree 생성 참고)
cd /Users/1111207/Documents/orion/git-worktrees/{type}/{name}
git add ... && git commit -m "..."

# 2) MR 생성 전 — diff가 있는지 확인 (비어 있으면 MR 만들지 말 것)
git fetch origin
git log --oneline origin/main..HEAD
git diff --stat origin/main...HEAD

# 3) 원격 push + GitLab MR
git push -u origin {type}/{name}
# glab 또는 GitLab UI: source={type}/{name} → target=main
# Changes 탭에 diff 확인 후 Merge (또는 glab mr merge)

# 4) 로컬 main 동기화 — pull만 (로컬 merge 아님)
cd /Users/1111207/Documents/orion
git checkout main && git pull origin main
```

**에이전트·Build and Test**: MR 본문·게이트는 `common/jira-integration.md`, `.cursor/rules/workflow.mdc` §Remote workflow gates, `aidlc-build-and-test` Step 11.

**금지 (MR Changes 0의 흔한 원인)**:
- `main`에 직접 커밋·push 한 뒤 MR 생성
- 로컬 `git merge --no-ff {type}/{name}` on `main` 후 MR 생성
- 이미 GitLab에서 머지된 브랜치로 MR을 다시 열기

---

## Deprecated: 로컬 main `--no-ff` 머지

아래 절차는 **사용하지 않는다** (GitLab MR SSOT와 충돌하여 MR에 변경이 없게 보임).

<details>
<summary>레거시 — 참고용만</summary>

```bash
git push -u origin {type}/{name}
cd /Users/1111207/Documents/orion
git merge --no-ff {type}/{name} -m "Merge {type}/{name} → main"
git push origin main
```

긴급 hotfix 등 MR 없이 반영이 필요하면 팀 합의 후에만 예외 적용.

</details>

---

## 머지 후 정리 (선택)

```bash
# worktree 제거
git -C /Users/1111207/Documents/orion worktree remove \
  git-worktrees/{type}/{name}

# 로컬 브랜치 제거 (원격은 유지)
git branch -d {type}/{name}
```

---

## 현재 등록된 Worktrees 확인

```bash
git -C /Users/1111207/Documents/orion worktree list
```
