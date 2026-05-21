#!/usr/bin/env python3
"""
pre_tool_use.py — Minimal reference stub for the "before tool execution" hook.

Per-CLI event names that map to this hook:
  Claude Code : PreToolUse    (.claude/settings.json  → hooks.PreToolUse)
  Cursor      : preToolUse    (.cursor/hooks.json     → hooks.preToolUse)
  Gemini CLI  : BeforeTool    (.gemini/settings.json  → hooks.BeforeTool)
  Antigravity : (no hook system as of 2026-05)

Stdin : JSON event payload (see below for common fields).
Stdout: JSON {"permission":"allow"|"deny", "reason"?:str}.
Exit 0 = allow (default when stdout is empty or not valid JSON).

Common payload fields:
  tool_name  : str   — e.g. "Edit", "Bash", "mcp__tavily__search"
  tool_input : dict  — tool arguments
  session_id : str

To DENY a tool call, return:
  {"permission": "deny", "reason": "explain why"}
"""

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    tool_name = payload.get("tool_name", "")

    # --- Add your gate logic here ---
    # Example: deny writes to generated files
    # if tool_name in ("Edit", "Write"):
    #     path = payload.get("tool_input", {}).get("file_path", "")
    #     if path.startswith(".claude/") or path.startswith(".cursor/"):
    #         print(json.dumps({"permission": "deny", "reason": "Edit derived files via hub/ instead"}))
    #         return

    # Default: allow everything
    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
