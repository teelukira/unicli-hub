#!/usr/bin/env python3
"""code_location_guard.py — PreToolUse hook.

Prevents writing code/config files inside documentation-only directories.
Default protected directory: `aidlc-docs/` and `docs/`.

Schema support:
  - Claude Code: {"tool_input": {"file_path": "..."}}
  - Cursor:      {"toolInput": {"file_path": "..."}}
  - Gemini CLI:  {"tool_input": {"path": "..."}}
  - Kiro:        {"args": {"file_path": "..."}}
"""

from __future__ import annotations

import json
import sys

# Directory paths that should only contain markdown/documentation
DOCS_DIRECTORIES = {"aidlc-docs/", "docs/"}

CODE_EXTENSIONS = {
    ".java", ".kt", ".kts", ".groovy", ".scala",
    ".go", ".rs", ".py", ".rb", ".php",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".fs",
    ".js", ".jsx", ".ts", ".tsx",
    ".yml", ".yaml",
}

CODE_FILENAMES = {
    "Dockerfile", "pom.xml", "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts", "package.json",
}


def extract_path(payload: dict) -> str:
    def dig(d: dict, *keys: str) -> str:
        node = d
        for k in keys:
            if not isinstance(node, dict):
                return ""
            node = node.get(k, "")
        return node if isinstance(node, str) else ""

    for keys in (
        ("tool_input", "file_path"),
        ("tool_input", "path"),
        ("toolInput", "file_path"),
        ("toolInput", "path"),
        ("args", "file_path"),
        ("args", "path"),
    ):
        val = dig(payload, *keys)
        if val:
            return val
    return ""


def is_code_file(path: str) -> bool:
    from pathlib import Path
    p = Path(path)
    if p.name in CODE_FILENAMES:
        return True
    return p.suffix.lower() in CODE_EXTENSIONS


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = extract_path(payload)
    if not path:
        return 0

    # Normalize: strip leading /.../<repo>/ prefix, keep relative portion
    normalized = path.replace("\\", "/")
    
    in_docs = any(d in normalized for d in DOCS_DIRECTORIES)
    if not in_docs:
        return 0

    if not is_code_file(path):
        return 0

    result = {
        "permission": "deny",
        "user_message": (
            f"Rule: Documentation directories ({', '.join(DOCS_DIRECTORIES)}) should only contain markdown files. "
            f"Please move code or configuration files to the workspace root: {path}"
        ),
        "agent_message": (
            f"Rule: Documentation directories ({', '.join(DOCS_DIRECTORIES)}) should only contain markdown files. "
            f"Please move code or configuration files to the workspace root: {path}"
        ),
        "hookSpecificOutput": {
            "hookType": "PreToolUse",
            "permissionDecision": "block",
            "permissionDecisionReason": (
                f"Rule: Documentation directories should only contain markdown files. "
                f"Path: {path}"
            ),
        }
    }
    print(json.dumps(result))
    return 1


if __name__ == "__main__":
    sys.exit(main())
