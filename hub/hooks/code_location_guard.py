#!/usr/bin/env python3
"""code_location_guard.py — PreToolUse hook.

Prevents writing code/config files inside aidlc-docs/ (documentation only directory).
Ported from legacy aidlc-code-location-guard.sh.

Schema support:
  - Claude Code: {"tool_input": {"file_path": "..."}}
  - Cursor:      {"toolInput": {"file_path": "..."}}
  - Gemini CLI:  {"tool_input": {"path": "..."}}
  - Kiro:        {"args": {"file_path": "..."}}
"""

from __future__ import annotations

import json
import sys
import traceback

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


def allow() -> int:
    print(json.dumps({"permission": "allow"}))
    return 0


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return allow()

    path = extract_path(payload)
    if not path:
        return allow()

    # Normalize: strip leading /.../<repo>/ prefix, keep relative portion
    # Match if path contains aidlc-docs/
    normalized = path.replace("\\", "/")
    in_docs = "aidlc-docs/" in normalized
    if not in_docs:
        return allow()

    if not is_code_file(path):
        return allow()

    result = {
        "permission": "deny",
        "user_message": (
            f"AI-DLC rule: `aidlc-docs/`에는 문서(.md)만 둘 수 있습니다. "
            f"코드/설정 파일은 워크스페이스 루트로 이동하세요: {path}"
        ),
        "agent_message": (
            f"AI-DLC rule: `aidlc-docs/`에는 문서(.md)만 둘 수 있습니다. "
            f"코드/설정 파일은 워크스페이스 루트로 이동하세요: {path}"
        ),
        "hookSpecificOutput": {
            "hookType": "PreToolUse",
            "permissionDecision": "block",
            "permissionDecisionReason": (
                f"AI-DLC rule: aidlc-docs/ 에는 문서(.md)만 둘 수 있습니다. "
                f"코드/설정 파일은 워크스페이스 루트로 이동하세요: {path}"
            ),
        },
    }
    print(json.dumps(result))
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": (
                        "code_location_guard.py crashed; refusing edit until fixed. "
                        + traceback.format_exc(limit=5)
                    ),
                    "agent_message": "code_location_guard.py exception — see hook user_message",
                }
            )
        )
        raise SystemExit(1)
