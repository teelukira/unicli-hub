# Memory

Stefania Druga의 발표 내용을 바탕으로, AI 에이전트의 장시간 작업 효율을 높이기 위한 **'메모리 하니스(Memory Harness)' 구축 가이드**를 정리해 드립니다. 이 가이드는 에이전트가 긴 작업 중에 정보를 잊지 않고 정확한 판단을 내리도록 돕습니다.

### 1. 핵심 설계 원칙: 쓰기·관리·읽기 루프 (3:10)
메모리를 단순한 데이터베이스로 보지 말고, 에이전트를 둘러싼 **제어 루프**로 설계해야 합니다.
* **쓰기 (Write):** 에이전트가 작업을 수행하면서 발생하는 중요한 결정 사항들을 기록합니다.
* **관리 (Manage):** 데이터의 중요도와 순서를 정렬하고 관리합니다.
* **읽기 (Read):** 필요할 때 적절한 정보를 인출합니다.

### 2. 하니스 구조 설계 (3:37)
에이전트의 구조를 세 부분으로 나누어 메모리를 최적화합니다.
* **코어 (Core):** 에이전트가 항상 참조해야 하는 핵심 작업 흔적(Traces).
* **회상 블록 (Recall):** 다양한 정책을 실험할 수 있는 곳으로, 이번 실험에서는 **'순위 기반 결정 장부(Ranked Decisions Ledger)'**가 가장 우수한 성능을 보였습니다 (7:46).
* **아카이브 (Archive):** 세션을 넘나들며 정보를 보존하는 저장소.

### 3. 성공적인 운영을 위한 전략
* **작업의 성격 파악 (5:45):** 작업이 에이전트의 컨텍스트 윈도우 내에서 모두 처리 가능하다면 메모리는 비용만 추가할 뿐입니다. 맥락이 길어지고 정보가 누락되는 '장기 작업'에만 메모리 하니스를 적용하세요.
* **회상 정책(Recall Policy)을 핵심 지표로 관리 (9:42):** 나쁜 메모리는 토큰을 낭비하고 에이전트를 잘못된 방향으로 이끕니다. 단순히 RAG를 쓰는 것보다, 단계별로 에이전트가 내린 결정의 우선순위를 매기는 방식이 더 효과적입니다 (9:15).
* **로컬 환경 활용 (10:59):** 로컬 모델을 사용하면 데이터 흐름과 평가 과정을 완전히 제어할 수 있어 '소버린 AI' 구현에 유리합니다. 단, 직렬 처리로 인해 시간이 소요될 수 있으므로 하드웨어 환경(예: M3 Ultra)을 충분히 고려해야 합니다 (2:39).

이 가이드를 따라 에이전트의 메모리 구조를 설계하면, 장시간 프로젝트에서도 망각 없이 일관된 성능을 유지할 수 있습니다.

`.unicli-rules/memory/` is the **canonical seed** for durable project facts. Its contents are propagated by `sync.sh` to each CLI's memory or context location.

## How each CLI consumes memory

| CLI | Mechanism |
|-----|-----------|
| Claude Code | Imported into `CLAUDE.md` via `@./.unicli-rules/memory/*.md` |
| Cursor | Exposed as `.cursor/rules/memory.mdc` with `alwaysApply: true` |
| Kiro | Accessible via the `.kiro/unicli-rules` symlink and copied to `.kiro/steering/03-memory.md` |
| Codex | Prepended to root `AGENTS.md` (Codex reads up to `project_doc_max_bytes`, so important facts are placed first) |
| Grok | Embedded in root `AGENTS.md` and copied to `.grok/rules/02-memory.md` |

## How to edit

1. Edit the files in this directory directly.
2. Run `./sync.sh --fix`.
3. Restart the CLI (or open a new session) to pick up the new context.

## Files

- `project-facts.md` — durable project facts (team, repo, load-bearing decisions)
- `conventions.md` — coding conventions, naming, directory layout
- `ranked-decisions.md` — Ranked Decisions Ledger (Recall)
- `glossary.md` — domain terminology (Archive)
