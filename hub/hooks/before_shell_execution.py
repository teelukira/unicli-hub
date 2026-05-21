#!/usr/bin/env python3
"""
before_shell_execution.py — Minimal reference stub for shell command gate.

Per-CLI event names that map to this hook:
  Claude Code : (no built-in shell gate — use PreToolUse with matcher "Bash")
  Cursor      : beforeShellExecution  (.cursor/hooks.json → hooks.beforeShellExecution)
  Gemini CLI  : (no shell-specific event — use BeforeTool)
  Antigravity : (no hook system as of 2026-05)

Stdin : JSON event payload.
  command    : str  — the shell command about to run
  session_id : str

Stdout: JSON {"permission":"allow"|"deny", "reason"?:str}.
"""

import json
import sys

# Patterns that should prompt a deny (customize for your project)
SENSITIVE_PATTERNS = [
    ".env",
    "id_rsa",
    "credentials",
    "/etc/passwd",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    command = payload.get("command", "")

    # --- Add your shell gate logic here ---
    # Example: block commands that touch sensitive files
    # for pattern in SENSITIVE_PATTERNS:
    #     if pattern in command:
    #         print(json.dumps({"permission": "deny", "reason": f"Command touches sensitive path: {pattern}"}))
    #         return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
