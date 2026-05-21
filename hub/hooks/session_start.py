#!/usr/bin/env python3
"""
session_start.py — Minimal reference stub for the session-start hook.

Per-CLI event names that map to this hook:
  Claude Code : SessionStart  (.claude/settings.json → hooks.SessionStart)
  Cursor      : (no direct equivalent; use postToolUse on first tool)
  Gemini CLI  : (no session-start event as of 2026-05)
  Antigravity : (no hook system as of 2026-05)

Called once when a new AI session begins.
Stdin : JSON event payload (may be empty or minimal).
Stdout: str — injected as additional context at session start (Claude Code only).

Use this hook to:
  - Inject project context / memory into the session
  - Check for required environment variables
  - Log session start for audit
"""

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    # --- Add your session-start logic here ---
    # Example: inject project memory as context
    # memory_file = pathlib.Path("hub/memory/project-facts.md")
    # if memory_file.exists():
    #     print(memory_file.read_text())
    #     return

    # Default: no additional context injected
    pass


if __name__ == "__main__":
    main()
