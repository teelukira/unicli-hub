#!/usr/bin/env python3
"""auto_sync.py — PostToolUse hook.

When the agent writes to any file under `hub/**`, this hook
runs `sync.sh --fix` so every derived CLI directory stays in sync.
Runs silently (exit 0) for writes outside the canonical tree or if
already running within a hook to avoid infinite loops.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CANONICAL_PREFIXES = (
    "hub/core-workflow.md",
    "hub/project-context.md",
    "hub/agents/",
    "hub/skills/",
    "hub/memory/",
    "hub/common/",
    "hub/templates/",
)


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


def main() -> int:
    # 0. Recursion Guard: prevent hang if we're already in a sync/hook process
    if os.environ.get("UNICLI_HOOK_ACTIVE") == "1":
        return 0
    os.environ["UNICLI_HOOK_ACTIVE"] = "1"

    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    changed = extract_path(payload)
    if not changed:
        return 0

    if not any(prefix in changed for prefix in CANONICAL_PREFIXES):
        return 0

    hook_dir = Path(__file__).resolve().parent
    root = hook_dir.parent.parent
    sync_script = root / "sync.sh"

    if not sync_script.is_file() or not os.access(sync_script, os.X_OK):
        print(
            f"auto-sync: sync.sh not found or not executable at {sync_script}",
            file=sys.stderr,
        )
        return 0

    print(f"auto-sync: canonical file changed ({changed}) — running sync.sh --fix")
    result = subprocess.run([str(sync_script), "--fix"], cwd=str(root))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
