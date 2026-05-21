#!/usr/bin/env python3
"""
post_tool_use.py — Minimal reference stub for the "after tool execution" hook.

Per-CLI event names that map to this hook:
  Claude Code : PostToolUse   (.claude/settings.json  → hooks.PostToolUse)
  Cursor      : postToolUse   (.cursor/hooks.json     → hooks.postToolUse)
  Gemini CLI  : AfterTool     (.gemini/settings.json  → hooks.AfterTool)
  Antigravity : (no hook system as of 2026-05)

Stdin : JSON event payload.
Stdout: (ignored by most CLIs for post hooks — use for logging only).

Common payload fields:
  tool_name   : str  — tool that just executed
  tool_input  : dict — arguments passed to the tool
  tool_result : any  — result returned by the tool
  session_id  : str
"""

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    tool_name = payload.get("tool_name", "")

    # --- Add your post-execution logic here ---
    # Example: trigger fanout sync after hub/ edits
    # if tool_name in ("Edit", "Write"):
    #     path = payload.get("tool_input", {}).get("file_path", "")
    #     if "/hub/" in path:
    #         import subprocess
    #         subprocess.run(["./sync.sh", "--fix"], capture_output=True)

    # Minimal: just log to stderr (visible in Claude Code's hook error output)
    print(f"[post_tool_use] {tool_name}", file=sys.stderr)


if __name__ == "__main__":
    main()
