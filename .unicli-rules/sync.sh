#!/usr/bin/env bash
# sync.sh — Propagate .unicli-rules/ canonical source to all AI CLI targets.
# Usage:
#   ./sync.sh              # regenerate all derived files (same as --fix)
#   ./sync.sh --fix        # regenerate all derived files
#   ./sync.sh --check      # CI mode: exit 1 if any derived file is out of sync
#   ./sync.sh --install-codex-prompts   # also install Codex prompts to ~/.codex/prompts/

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CANONICAL="${ROOT}/.unicli-rules"

CLAUDE_DIR="${ROOT}/.claude"
CURSOR_DIR="${ROOT}/.cursor"
GEMINI_DIR="${ROOT}/.gemini"
KIRO_DIR="${ROOT}/.kiro"
CODEX_DIR="${ROOT}/.codex"

# ---------------------------------------------------------------------------
# Mode
# ---------------------------------------------------------------------------
MODE="fix"
INSTALL_CODEX_PROMPTS=0
for arg in "$@"; do
  case "$arg" in
    --fix) MODE="fix" ;;
    --check) MODE="check" ;;
    --install-codex-prompts) INSTALL_CODEX_PROMPTS=1 ;;
    *) echo "Unknown arg: $arg" >&2; exit 2 ;;
  esac
done

DRIFT=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
check_source() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "FATAL: canonical source missing: $f" >&2
    exit 2
  fi
}

# Read file contents safely
read_file() { cat "$1"; }

# Write content to a file, with drift detection in --check mode
compare_or_write() {
  local target="$1"
  local content="$2"
  if [[ "$MODE" == "check" ]]; then
    if [[ ! -f "$target" ]] || ! diff -q <(printf '%s' "$content") "$target" >/dev/null 2>&1; then
      echo "DRIFT: $target"
      DRIFT=1
      if [[ -f "$target" ]]; then
        diff <(printf '%s' "$content") "$target" | head -n 20 || true
      fi
    fi
  else
    mkdir -p "$(dirname "$target")"
    printf '%s' "$content" > "$target"
    echo "wrote: ${target#${ROOT}/}"
  fi
}

# Assemble a template: replace {{PROJECT_CONTEXT}}, {{CORE_WORKFLOW}}, {{MEMORY}}
assemble_template() {
  local tmpl="$1"
  local tmpl_content project_ctx core_wf memory_block
  tmpl_content="$(cat "$tmpl")"
  project_ctx="$(cat "${CANONICAL}/project-context.md")"
  core_wf="$(cat "${CANONICAL}/core-workflow.md")"

  # Build memory block by concatenating memory files (excluding README.md)
  memory_block=""
  for mf in "${CANONICAL}/memory/project-facts.md" "${CANONICAL}/memory/conventions.md" "${CANONICAL}/memory/glossary.md"; do
    if [[ -f "$mf" ]]; then
      memory_block+="$(cat "$mf")"$'\n\n'
    fi
  done

  # Substitute placeholders using awk for multi-line safety
  python3 - "$tmpl_content" "$project_ctx" "$core_wf" "$memory_block" <<'PY'
import sys
tmpl, ctx, wf, mem = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
out = tmpl.replace("{{PROJECT_CONTEXT}}", ctx).replace("{{CORE_WORKFLOW}}", wf).replace("{{MEMORY}}", mem)
sys.stdout.write(out)
PY
}

ensure_symlink() {
  local src="$1" dst="$2"
  if [[ "$MODE" == "check" ]]; then
    if [[ ! -L "$dst" ]] || [[ "$(readlink "$dst")" != "$src" ]]; then
      echo "DRIFT: symlink $dst -> $src"
      DRIFT=1
    fi
  else
    mkdir -p "$(dirname "$dst")"
    if [[ -L "$dst" ]] && [[ "$(readlink "$dst")" == "$src" ]]; then
      return
    fi
    rm -rf "$dst"
    ln -s "$src" "$dst"
    echo "symlink: ${dst#${ROOT}/} -> $src"
  fi
}

copy_with_prefix() {
  local src="$1" dst="$2" prefix="$3"
  check_source "$src"
  local body content
  body="$(cat "$src")"
  content="${prefix}${body}"
  compare_or_write "$dst" "$content"
}

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
check_source "${CANONICAL}/core-workflow.md"
check_source "${CANONICAL}/project-context.md"
check_source "${CANONICAL}/templates/CLAUDE.md.tmpl"
check_source "${CANONICAL}/templates/GEMINI.md.tmpl"
check_source "${CANONICAL}/templates/AGENTS.md.tmpl"

# ---------------------------------------------------------------------------
# [1] CLAUDE.md (root)
# ---------------------------------------------------------------------------
echo "[1] CLAUDE.md"
claude_md="$(assemble_template "${CANONICAL}/templates/CLAUDE.md.tmpl")"
compare_or_write "${ROOT}/CLAUDE.md" "$claude_md"

# ---------------------------------------------------------------------------
# [2] AGENTS.md (root)
# ---------------------------------------------------------------------------
echo "[2] AGENTS.md"
agents_md="$(assemble_template "${CANONICAL}/templates/AGENTS.md.tmpl")"
compare_or_write "${ROOT}/AGENTS.md" "$agents_md"

# ---------------------------------------------------------------------------
# [3] GEMINI.md
# ---------------------------------------------------------------------------
echo "[3] .gemini/GEMINI.md"
gemini_md="$(assemble_template "${CANONICAL}/templates/GEMINI.md.tmpl")"
compare_or_write "${GEMINI_DIR}/GEMINI.md" "$gemini_md"

# ---------------------------------------------------------------------------
# [4] Cursor rules (workflow + context)
# ---------------------------------------------------------------------------
echo "[4] .cursor/rules/"
cursor_wf_fm="$(cat "${CANONICAL}/templates/frontmatter/cursor-workflow.yaml")"
cursor_wf_body="$(cat "${CANONICAL}/core-workflow.md")"
compare_or_write "${CURSOR_DIR}/rules/workflow.mdc" "${cursor_wf_fm}
${cursor_wf_body}
"

cursor_ctx_fm="$(cat "${CANONICAL}/templates/frontmatter/cursor-context.yaml")"
cursor_ctx_body="$(cat "${CANONICAL}/project-context.md")"
compare_or_write "${CURSOR_DIR}/rules/project-context.mdc" "${cursor_ctx_fm}
${cursor_ctx_body}
"

# Memory rule (always apply)
memory_content=""
for mf in "${CANONICAL}/memory/project-facts.md" "${CANONICAL}/memory/conventions.md" "${CANONICAL}/memory/glossary.md"; do
  [[ -f "$mf" ]] && memory_content+="$(cat "$mf")"$'\n\n'
done
cursor_mem_fm='---
description: Project memory (durable facts, conventions, glossary). Generated from .unicli-rules/memory/. Do not edit directly.
globs:
  - "**/*"
alwaysApply: true
---
'
compare_or_write "${CURSOR_DIR}/rules/memory.mdc" "${cursor_mem_fm}
${memory_content}"

# ---------------------------------------------------------------------------
# [5] Kiro symlinks
# ---------------------------------------------------------------------------
echo "[5] .kiro/ symlinks"
ensure_symlink "../.unicli-rules" "${KIRO_DIR}/unicli-rules"
ensure_symlink "../../.unicli-rules/agents" "${KIRO_DIR}/agents/prompts"

# ---------------------------------------------------------------------------
# [6] Kiro steering (copies)
# ---------------------------------------------------------------------------
echo "[6] .kiro/steering/"
compare_or_write "${KIRO_DIR}/steering/01-project-context.md" "$(cat "${CANONICAL}/project-context.md")
"
compare_or_write "${KIRO_DIR}/steering/02-core-workflow.md" "$(cat "${CANONICAL}/core-workflow.md")
"
compare_or_write "${KIRO_DIR}/steering/03-memory.md" "${memory_content}"

# ---------------------------------------------------------------------------
# Agent fan-out helpers
# ---------------------------------------------------------------------------
SHARED_AGENTS=(researcher codegen reviewer)

# Claude model assignment
declare -A CLAUDE_MODEL=(
  [researcher]="claude-opus-4-7"
  [codegen]="claude-sonnet-4-6"
  [reviewer]="claude-opus-4-7"
)

# Gemini model assignment
declare -A GEMINI_MODEL=(
  [researcher]="gemini-3-pro-preview"
  [codegen]="gemini-3-pro-preview"
  [reviewer]="gemini-3-pro-preview"
)

# Tool allowlists per agent (bullet list lines)
claude_tools() {
  case "$1" in
    researcher) printf '  - Read\n  - Glob\n  - Grep\n  - WebSearch\n  - WebFetch\n' ;;
    codegen)    printf '  - Read\n  - Edit\n  - Write\n  - Glob\n  - Grep\n  - Bash\n' ;;
    reviewer)   printf '  - Read\n  - Glob\n  - Grep\n  - Bash\n' ;;
  esac
}

agent_description() {
  case "$1" in
    researcher) echo "Investigate code and external sources; produce evidence-based summaries without speculation." ;;
    codegen)    echo "Implement approved plans with minimal, focused edits; reuse existing utilities; run tests." ;;
    reviewer)   echo "Independently review changes for correctness, security, reuse, and convention compliance." ;;
  esac
}

# ---------------------------------------------------------------------------
# [7] .claude/agents/
# ---------------------------------------------------------------------------
echo "[7] .claude/agents/"
for a in "${SHARED_AGENTS[@]}"; do
  src="${CANONICAL}/agents/${a}.md"
  check_source "$src"
  tools="$(claude_tools "$a")"
  desc="$(agent_description "$a")"
  model="${CLAUDE_MODEL[$a]}"
  fm="---
name: ${a}
description: ${desc}
model: ${model}
tools:
${tools}---
"
  body="$(cat "$src")"
  compare_or_write "${CLAUDE_DIR}/agents/${a}.md" "${fm}
${body}
"
done

# ---------------------------------------------------------------------------
# [8] .cursor/agents/
# ---------------------------------------------------------------------------
echo "[8] .cursor/agents/"
for a in "${SHARED_AGENTS[@]}"; do
  src="${CANONICAL}/agents/${a}.md"
  desc="$(agent_description "$a")"
  fm="---
description: ${desc}
source: .unicli-rules/agents/${a}.md
---
"
  body="$(cat "$src")"
  compare_or_write "${CURSOR_DIR}/agents/${a}.md" "${fm}
${body}
"
done

# ---------------------------------------------------------------------------
# [9] .gemini/agents/
# ---------------------------------------------------------------------------
echo "[9] .gemini/agents/"
for a in "${SHARED_AGENTS[@]}"; do
  src="${CANONICAL}/agents/${a}.md"
  desc="$(agent_description "$a")"
  model="${GEMINI_MODEL[$a]}"
  fm="---
name: ${a}
description: ${desc}
model: ${model}
---
"
  body="$(cat "$src")"
  compare_or_write "${GEMINI_DIR}/agents/${a}.md" "${fm}
${body}
"
done

# ---------------------------------------------------------------------------
# [10] .codex/prompts/ (plain markdown — Codex slash commands)
# ---------------------------------------------------------------------------
echo "[10] .codex/prompts/"
for a in "${SHARED_AGENTS[@]}"; do
  src="${CANONICAL}/agents/${a}.md"
  body="$(cat "$src")"
  compare_or_write "${CODEX_DIR}/prompts/${a}.md" "${body}
"
done

# Optional: install Codex prompts to user directory so slash commands work globally
if [[ "$INSTALL_CODEX_PROMPTS" == "1" ]] && [[ "$MODE" == "fix" ]]; then
  echo "[10+] installing Codex prompts to ~/.codex/prompts/"
  mkdir -p "${HOME}/.codex/prompts"
  for a in "${SHARED_AGENTS[@]}"; do
    cp "${CODEX_DIR}/prompts/${a}.md" "${HOME}/.codex/prompts/unicli-${a}.md"
    echo "installed: ~/.codex/prompts/unicli-${a}.md"
  done
fi

# ---------------------------------------------------------------------------
# [11] Skills fan-out
# ---------------------------------------------------------------------------
echo "[11] skills fan-out"
for skill_path in "${CANONICAL}/skills/"*.md; do
  [[ -e "$skill_path" ]] || continue
  skill_file="$(basename "$skill_path")"
  skill_name="${skill_file%.md}"
  body="$(cat "$skill_path")"

  # Gemini: .gemini/skills/<name>/SKILL.md
  compare_or_write "${GEMINI_DIR}/skills/${skill_name}/SKILL.md" "${body}
"
  # Cursor: .cursor/skills/<name>/SKILL.md
  compare_or_write "${CURSOR_DIR}/skills/${skill_name}/SKILL.md" "${body}
"
done

# ---------------------------------------------------------------------------
# [12] Cursor hooks symlinks (Python)
# ---------------------------------------------------------------------------
echo "[12] .cursor/hooks/ symlinks"
for h in "${CANONICAL}/hooks/"*.py; do
  [[ -e "$h" ]] || continue
  hname="$(basename "$h")"
  ensure_symlink "../../.unicli-rules/hooks/${hname}" "${CURSOR_DIR}/hooks/${hname}"
done

# ---------------------------------------------------------------------------
# [13] MCP config fan-out (all 5 CLIs)
# ---------------------------------------------------------------------------
echo "[13] MCP config fan-out"
python3 "${CANONICAL}/hooks/render_mcp.py" "--${MODE}" || {
  if [[ "$MODE" == "check" ]]; then DRIFT=1; else exit 1; fi
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
if [[ "$MODE" == "check" ]]; then
  if [[ $DRIFT -eq 0 ]]; then
    echo "✓ all derived files in sync"
    exit 0
  else
    echo "✗ drift detected — run: ./.unicli-rules/sync.sh --fix"
    exit 1
  fi
else
  echo "✓ sync complete"
fi
