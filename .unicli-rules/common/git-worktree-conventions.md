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
| `feature/` | 신규 AI-DLC 유닛, 새 기능 구현 | `feature/ai-dlc-u17-search-data-seeding` |
| `fix/` | 버그 수정, UX 교정 | `fix/u17-frontend-resource-mgmt-bugs`, `fix/u17-frontend-ux` |
| `chore/` | 문서 정리, 리팩토링, 비코드 작업 | `chore/aidlc-docs-ssot-consolidation` |

**규칙**: 코드 변경(feature/fix)과 문서/인프라 변경(chore)은 브랜치를 분리.

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
2. **main worktree는 그대로** — main의 uncommitted 변경은 main 체크아웃에 남음. 신규 worktree는 마지막 커밋(HEAD) 기준 clean state로 시작.
3. **한 worktree = 한 관심사** — feature + fix 혼합 금지.
4. **worktree 내 작업** — `cd git-worktrees/{type}/{name}` 후 작업. git 명령은 해당 디렉토리에서 실행.

---

## 원격 푸시 + main 머지 절차

```bash
# 1. 브랜치 원격 푸시 (머지 전에 먼저)
git -C /Users/1111207/Documents/orion push -u origin {type}/{name}

# 2. main worktree에서 --no-ff 머지
cd /Users/1111207/Documents/orion
git merge --no-ff {type}/{name} -m "$(cat <<'EOF'
Merge {type}/{name} → main

{변경 내용 요약}

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"

# 3. main 원격 푸시
git push origin main
```

**--no-ff 이유**: merge commit을 남겨 브랜치 병합 히스토리를 명확히 추적.

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
