#!/usr/bin/env python3
"""
before_mcp_execution.py — Minimal reference stub for MCP tool gate.

Per-CLI event names that map to this hook:
  Claude Code : PreToolUse with matcher "mcp__*"  (.claude/settings.json)
  Cursor      : beforeMCPExecution                (.cursor/hooks.json)
  Gemini CLI  : BeforeTool (MCP calls are regular tool calls in Gemini)
  Antigravity : (no hook system as of 2026-05)

Stdin : JSON event payload.
  server_name : str  — MCP server (e.g. "mcp-atlassian")
  tool_name   : str  — MCP tool   (e.g. "jira_create_issue")
  tool_input  : dict — arguments
  session_id  : str

Stdout: JSON {"permission":"allow"|"deny", "reason"?:str}.
"""

import json
import sys

# MCP tools that require explicit user confirmation before running
GATED_TOOLS = [
    # "jira_create_issue",
    # "jira_transition_issue",
    # "gitlab__create_merge_request",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    tool_name = payload.get("tool_name", "")

    # --- Add your MCP gate logic here ---
    # if tool_name in GATED_TOOLS:
    #     print(json.dumps({"permission": "deny", "reason": f"{tool_name} requires human review first"}))
    #     return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
