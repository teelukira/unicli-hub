#!/bin/bash
# sync.sh — Unified UniCLI-Hub Sync Script (SSOT Framework)
# 
# Usage:
#   ./sync.sh --fix    [default] Sync all targets from hub/
#   ./sync.sh --check   Verify sync (exit 1 on drift)
#   ./sync.sh --fix --target=codex

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_SCRIPTS="$ROOT/.unicli-hub/scripts"

MODE="fix"
TARGET_FLAG=""
for arg in "$@"; do
    if [[ "$arg" == "--check" ]]; then MODE="check"; fi
    if [[ "$arg" == --target=* ]]; then TARGET_FLAG="$arg"; fi
done

echo "--- UniCLI-Hub Sync ($MODE${TARGET_FLAG:+, $TARGET_FLAG}) ---"

# Clean up legacy Antigravity structures to avoid conflicts
if [ "$MODE" = "fix" ] && [ -z "$TARGET_FLAG" ]; then
    if [ -d "$ROOT/.agents/plugins" ]; then
        echo "Cleaning legacy plugins directory..."
        rm -rf "$ROOT/.agents/plugins"
    fi
    if [ -d "$ROOT/.antigravitycli" ]; then
        echo "Cleaning legacy .antigravitycli directory..."
        rm -rf "$ROOT/.antigravitycli"
    fi
    if [ -d "$ROOT/.agy" ]; then
        echo "Cleaning legacy .agy directory..."
        rm -rf "$ROOT/.agy"
    fi
    if [ -d "$ROOT/.gemini" ]; then
        echo "Cleaning legacy .gemini directory..."
        rm -rf "$ROOT/.gemini"
    fi
    if [ -f "$ROOT/GEMINI.md" ]; then
        echo "Removing legacy GEMINI.md..."
        rm -f "$ROOT/GEMINI.md"
    fi
    if [ -f "$ROOT/AGY.md" ]; then
        echo "Removing legacy AGY.md..."
        rm -f "$ROOT/AGY.md"
    fi
    if [ -d "$ROOT/.cursor/hooks" ]; then
        echo "Cleaning legacy Cursor hooks directory..."
        rm -rf "$ROOT/.cursor/hooks"
    fi
    find "$ROOT/hub" "$ROOT/.cursor" "$ROOT/.agents" "$ROOT/.claude" -type d -name "__pycache__" -prune -exec rm -rf {} +
fi

# 1. Ensure Python dependencies if any (usually built-in)
# python3 -m pip install -q ...

# 2. Render Agents
python3 "$CORE_SCRIPTS/render_agents.py" --$MODE $TARGET_FLAG

# 3. Render Skills
python3 "$CORE_SCRIPTS/render_skills.py" --$MODE $TARGET_FLAG

# 3.5 Render static declared fan-out copies
python3 "$CORE_SCRIPTS/render_static.py" --$MODE $TARGET_FLAG

# 4. Render Hooks and Settings
python3 "$CORE_SCRIPTS/render_hooks.py" --$MODE $TARGET_FLAG

# 5. Render MCP
python3 "$CORE_SCRIPTS/render_mcp.py" --$MODE $TARGET_FLAG

# 6. Render Entry Point Templates (CLAUDE.md, AGENTS.md)
python3 "$CORE_SCRIPTS/render_templates.py" --$MODE $TARGET_FLAG

echo "--- Sync Complete ---"
