#!/usr/bin/env python3
"""before_shell_execution.py — UniCLI-Hub shell execution hook.

Checks for sensitive files/credentials before command execution.
"""

from __future__ import annotations

import json
import sys

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

    command = payload.get("command", "") or payload.get("shellCommand", "")
    for pattern in SENSITIVE_PATTERNS:
        if pattern in command:
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "reason": f"Command touches sensitive path: {pattern}",
                    }
                )
            )
            return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
