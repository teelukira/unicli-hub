#!/usr/bin/env python3
"""pre_skill_sync.py — Run sync.sh before reading skill sources so derived SKILL.md files stay fresh.

Triggered by Cursor (beforeReadFile / Read) and Gemini CLI (BeforeTool read_file).
Exits 0 always unless sync fails and the caller treats non-zero specially; prefer failOpen.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from fnmatch import fnmatch
from pathlib import Path

DEBOUNCE_SEC = 5.0
STAMP_NAME = ".pre_skill_sync_stamp"


def extract_path(payload: dict) -> str:
    for key in ("file_path", "path", "filePath"):
        v = payload.get(key)
        if isinstance(v, str) and v:
            return v

    for ti_key in ("tool_input", "toolInput", "args"):
        node = payload.get(ti_key)
        if isinstance(node, dict):
            for key in ("file_path", "path", "filePath"):
                v = node.get(key)
                if isinstance(v, str) and v:
                    return v

    def dig(d: dict, *keys: str) -> str:
        node: object = d
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


def normalize(path: str) -> str:
    if not path:
        return ""
    marker = "/unicli-hub/"
    if marker in path:
        path = path.split(marker, 1)[1]
    return path.lstrip("/")


def matches_skill_read(rel: str) -> bool:
    if not rel:
        return False
    if fnmatch(rel, ".cursor/skills/*/SKILL.md"):
        return True
    if fnmatch(rel, ".gemini/skills/*/SKILL.md"):
        return True
    if fnmatch(rel, ".unicli-rules/skills/*.md"):
        return True
    return False


def within_debounce(stamp_path: Path) -> bool:
    if not stamp_path.is_file():
        return False
    try:
        last = float(stamp_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    return (time.time() - last) < DEBOUNCE_SEC


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    target = extract_path(payload)
    rel = normalize(target)
    if not rel or not matches_skill_read(rel):
        return 0

    hook_dir = Path(__file__).resolve().parent
    root = hook_dir.parent.parent
    sync_script = root / ".unicli-rules" / "sync.sh"
    stamp_path = hook_dir.parent / STAMP_NAME

    if not sync_script.is_file() or not os.access(sync_script, os.X_OK):
        print(
            f"pre-skill-sync: sync.sh not found or not executable at {sync_script}",
            file=sys.stderr,
        )
        return 0

    if within_debounce(stamp_path):
        return 0

    print(f"pre-skill-sync: skill read ({rel}) — running sync.sh --fix", file=sys.stderr)
    result = subprocess.run([str(sync_script), "--fix"], cwd=str(root))
    if result.returncode == 0:
        try:
            stamp_path.write_text(str(time.time()), encoding="utf-8")
        except OSError:
            pass
    elif result.returncode != 0:
        print(
            f"pre-skill-sync: sync.sh exited {result.returncode} (continuing; fail-open)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
