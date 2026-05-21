#!/usr/bin/env python3
"""
post_tool_use.py — Auto-runs sync.sh after hub/ edits (fanout enforcement).

Per-CLI event names that map to this hook:
  Claude Code : PostToolUse   (.claude/settings.json  → hooks.PostToolUse)
  Cursor      : postToolUse   (.cursor/hooks.json     → hooks.postToolUse)
  Gemini CLI  : AfterTool     (.gemini/settings.json  → hooks.AfterTool)
  Antigravity : (no hook system as of 2026-05)

Stdin : JSON event payload.
  tool_name   : str  — tool that just executed
  tool_input  : dict — arguments passed to the tool
  tool_result : any  — result returned by the tool
  session_id  : str

Stdout: (ignored by most CLIs for post hooks).
"""

import json
import subprocess
import sys
import pathlib

# Trigger sync when any of these directory prefixes are edited
SYNC_TRIGGER_DIRS = ["hub/"]

# Locate repo root (parent of the directory containing this script)
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # hub/hooks/ → hub/ → repo root
SYNC_SCRIPT = REPO_ROOT / "sync.sh"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        return

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    # Normalize to relative path from repo root
    try:
        rel = pathlib.Path(file_path).resolve().relative_to(REPO_ROOT)
        rel_str = str(rel)
    except ValueError:
        return  # outside repo

    # Check if the edited file is under a sync-trigger directory
    if not any(rel_str.startswith(prefix) for prefix in SYNC_TRIGGER_DIRS):
        return

    # Run sync.sh --fix to fanout hub/ changes to derived CLI directories
    result = subprocess.run(
        ["/bin/bash", str(SYNC_SCRIPT), "--fix"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[post_tool_use] sync.sh --fix failed:\n{result.stderr}", file=sys.stderr)
    else:
        lines = [l for l in result.stdout.splitlines() if l.strip()]
        if lines:
            print(f"[post_tool_use] synced: {', '.join(lines)}", file=sys.stderr)


if __name__ == "__main__":
    main()
