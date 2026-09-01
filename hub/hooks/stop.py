#!/usr/bin/env python3
"""
stop.py — Minimal reference stub for the session/agent stop hook.

Per-CLI event names that map to this hook:
  Claude Code : Stop          (.claude/settings.json → hooks.Stop)
  Cursor      : stop          (.cursor/hooks.json    → hooks.stop)
  Grok        : Stop          (.grok/hooks/unicli-hub.json → hooks.Stop)
  Gemini CLI  : (no stop event as of 2026-05)
  Antigravity : (no hook system as of 2026-05)

Called when the AI agent finishes responding or the session ends.
Stdin : JSON event payload.
  session_id : str
  reason     : str  — e.g. "user_request", "max_tokens"

Stdout: (ignored — use for side effects only).

Use this hook to:
  - Send a desktop/Slack notification that the agent is done
  - Save a session summary
  - Flush audit logs
"""

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    # --- Add your stop logic here ---
    # Example: macOS notification
    # import subprocess
    # subprocess.run(["osascript", "-e", 'display notification "Agent done" with title "unicli"'])

    # Example: log session end
    # print(f"[stop] session ended: {payload.get('session_id', 'unknown')}", file=sys.stderr)

    pass


if __name__ == "__main__":
    main()
