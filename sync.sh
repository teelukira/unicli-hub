#!/bin/bash
# sync.sh — Unified UniCLI-Hub Sync Script (SSOT Framework)
# 
# Usage:
#   ./sync.sh --fix    [default] Sync all targets from hub/
#   ./sync.sh --check   Verify sync (exit 1 on drift)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_SCRIPTS="$ROOT/.unicli-hub/scripts"

MODE="fix"
TARGET_FLAG=""
for arg in "$@"; do
    if [[ "$arg" == "--check" ]]; then MODE="check"; fi
    if [[ "$arg" == "--gemini" ]]; then TARGET_FLAG="--target=gemini"; fi
done

echo "--- UniCLI-Hub Sync ($MODE) ---"
if [[ -n "$TARGET_FLAG" ]]; then echo "Target: Gemini Only"; fi

# 1. Ensure Python dependencies if any (usually built-in)
# python3 -m pip install -q ...

# 2. Render Agents
python3 "$CORE_SCRIPTS/render_agents.py" --$MODE $TARGET_FLAG

# 3. Render Skills
python3 "$CORE_SCRIPTS/render_skills.py" --$MODE $TARGET_FLAG

# 4. Render Hooks and Settings
python3 "$CORE_SCRIPTS/render_hooks.py" --$MODE $TARGET_FLAG

# 5. Render MCP
python3 "$CORE_SCRIPTS/render_mcp.py" --$MODE $TARGET_FLAG

# 6. Render Entry Point Templates (CLAUDE.md, GEMINI.md, AGY.md, AGENTS.md)
python3 "$CORE_SCRIPTS/render_templates.py" --$MODE $TARGET_FLAG

echo "--- Sync Complete ---"
