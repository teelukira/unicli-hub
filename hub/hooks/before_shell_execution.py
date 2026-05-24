#!/usr/bin/env python3
"""
before_shell_execution.py - shell hook skeleton.

This framework keeps shell policy in code, not prose. Add project-specific
checks here or delegate to additional guard modules under hub/hooks/.
"""

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
            print(json.dumps({"permission": "deny", "reason": f"Command touches sensitive path: {pattern}"}))
            return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
