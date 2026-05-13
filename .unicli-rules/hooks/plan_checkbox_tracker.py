#!/usr/bin/env python3
"""plan_checkbox_tracker.py — PostToolUse hook.

After editing a plan file, prints a checkbox progress summary
so the agent can see how many steps are done vs remaining.

Schema support:
  - Claude Code: {"tool_input": {"file_path": "..."}}
  - Cursor:      {"toolInput": {"file_path": "..."}}
  - Gemini CLI:  {"tool_input": {"path": "..."}}
  - Kiro:        {"args": {"file_path": "..."}}
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# Matches any file ending in plan.md
PLAN_PATTERN = re.compile(r".*plan\.md$", re.IGNORECASE)


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


def count_checkboxes(content: str) -> tuple[int, int]:
    done = len(re.findall(r"- \[x\]", content, re.IGNORECASE))
    todo = len(re.findall(r"- \[ \]", content))
    return done, todo


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = extract_path(payload)
    if not path:
        return 0

    normalized = path.replace("\\", "/")
    if not PLAN_PATTERN.search(normalized):
        return 0

    # Resolve absolute path
    resolved = Path(path)
    if not resolved.is_absolute():
        # Try relative to repo root (two levels up from this hook file)
        repo_root = Path(__file__).resolve().parent.parent.parent
        resolved = repo_root / path

    if not resolved.is_file():
        return 0

    try:
        content = resolved.read_text(encoding="utf-8")
    except Exception:
        return 0
        
    done, todo = count_checkboxes(content)
    total = done + todo

    if total == 0:
        return 0

    pct = int(done / total * 100)
    print(
        f"[plan-checkbox-tracker] {done}/{total} steps done ({pct}%) — "
        f"{todo} remaining in {Path(path).name}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
