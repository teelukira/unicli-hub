#!/usr/bin/env python3
"""shell_sensitive_file_guard.py — beforeShellExecution hook.

Blocks shell-based mutations to sensitive state/audit/plan files so file-edit
hooks remain effective, and prevents push/merge when workflow rules are violated.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Sensitive files that should only be edited via file-edit tools (to trigger hooks)
SENSITIVE_FILES = ("aidlc-state.md", "audit.md", "state.md")
SENSITIVE_PATH_HINTS = (
    "aidlc-state.md",
    "audit.md",
    "state.md",
    "plan.md",
)

MUTATING_PATTERNS = (
    re.compile(r"\bsed\b.*\s-i\b"),
    re.compile(r"\bperl\b.*\s-i\b"),
    re.compile(r"\btee\b"),
    re.compile(r">>"),
    re.compile(r"(?<!2)>"),
    re.compile(r"\bpython(?:3)?\b.*\b(open|Path)\b", re.IGNORECASE),
)
PUSH_OR_MERGE = re.compile(r"\bgit\s+(push|merge)\b|\bgh\s+pr\s+create\b")


def dig(payload: dict, *keys: str) -> str:
    node = payload
    for key in keys:
        if not isinstance(node, dict):
            return ""
        node = node.get(key, "")
    return node if isinstance(node, str) else ""


def extract_command(payload: dict) -> str:
    for keys in (
        ("command",),
        ("shell_command",),
        ("shellCommand",),
        ("args", "command"),
        ("tool_input", "command"),
        ("toolInput", "command"),
    ):
        value = dig(payload, *keys)
        if value:
            return value
    return ""


def repo_root() -> Path:
    # Assuming the hook is in .unicli-rules/hooks/
    return Path(__file__).resolve().parent.parent.parent


def is_sensitive_shell_mutation(command: str) -> bool:
    if not any(path_hint in command for path_hint in SENSITIVE_PATH_HINTS):
        return False
    return any(pattern.search(command) for pattern in MUTATING_PATTERNS)


def block(reason: str) -> int:
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": reason,
                "agent_message": reason,
            }
        )
    )
    return 1


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    command = extract_command(payload)
    if not command:
        return 0

    if is_sensitive_shell_mutation(command):
        return block(
            "Shell block: Do not mutate sensitive state or plan files via shell (e.g., sed, tee, redirection). "
            "Use file edit tools so workflow hooks can validate the changes."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
