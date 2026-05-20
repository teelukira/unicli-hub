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
for arg in "$@"; do
    if [[ "$arg" == "--check" ]]; then MODE="check"; fi
done

echo "--- UniCLI-Hub Sync ($MODE) ---"

# 1. Ensure Python dependencies if any (usually built-in)
# python3 -m pip install -q ...

# 2. Render Agents
python3 "$CORE_SCRIPTS/render_agents.py" --$MODE

# 3. Render Skills
python3 "$CORE_SCRIPTS/render_skills.py" --$MODE

# 4. Render Hooks and Settings
python3 "$CORE_SCRIPTS/render_hooks.py" --$MODE

# 5. Render MCP
python3 "$CORE_SCRIPTS/render_mcp.py" --$MODE

# 6. Render Entry Point Templates (CLAUDE.md, GEMINI.md, AGY.md, AGENTS.md)
python3 "$CORE_SCRIPTS/render_templates.py" --$MODE

echo "--- Sync Complete ---"
