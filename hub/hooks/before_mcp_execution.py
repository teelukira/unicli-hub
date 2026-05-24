#!/usr/bin/env python3
"""
before_mcp_execution.py - MCP hook skeleton.

Keep MCP gate policy here or in imported guard modules. The default framework
allows all MCP tools; projects can add gated tool names below.
"""

import json
import sys

GATED_TOOLS = [
    # "jira_create_issue",
    # "jira_transition_issue",
    # "gitlab_create_merge_request",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    tool_name = payload.get("tool_name") or payload.get("toolName") or payload.get("name") or ""
    if tool_name in GATED_TOOLS:
        print(json.dumps({"permission": "deny", "reason": f"{tool_name} requires explicit project approval"}))
        return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
