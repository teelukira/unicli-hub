#!/usr/bin/env python3
"""state_audit.py — PostToolUse hook.

Detects edits to aidlc-docs/aidlc-state.md and appends a concise audit entry
to aidlc-docs/audit.md (never overwrites). Uses SHA-256 cache to avoid
duplicate entries on no-content-change saves.
Ported from legacy aidlc-state-audit.sh.

Schema support:
  - Claude Code: {"tool_input": {"file_path": "..."}}
  - Cursor:      {"toolInput": {"file_path": "..."}}
  - Gemini CLI:  {"tool_input": {"path": "..."}}
  - Kiro:        {"args": {"file_path": "..."}}
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


STATE_FILE_SUFFIX = "aidlc-docs/aidlc-state.md"
AUDIT_FILE_SUFFIX = "aidlc-docs/audit.md"
CACHE_FILENAME = "tgo-im-aidlc-state.sha256"


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


def is_state_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.endswith(STATE_FILE_SUFFIX)


def sha256_file(file: Path) -> str:
    h = hashlib.sha256()
    h.update(file.read_bytes())
    return h.hexdigest()


def get_diff_summary(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--unified=0", "--", "aidlc-docs/aidlc-state.md"],
            capture_output=True, text=True, timeout=10,
        )
        items = []
        for line in result.stdout.splitlines():
            if line.startswith(("+++", "---", "@@")):
                continue
            if line.startswith(("+", "-")):
                body = line[1:].strip()
                if body:
                    prefix = "added" if line.startswith("+") else "removed"
                    items.append(f"{prefix}: {body[:120]}")
            if len(items) >= 4:
                break
        return "; ".join(items) if items else ""
    except Exception:
        return ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = extract_path(payload)
    if not path or not is_state_file(path):
        return 0

    repo_root = Path(__file__).resolve().parent.parent.parent
    state_file = repo_root / "aidlc-docs" / "aidlc-state.md"
    audit_file = repo_root / "aidlc-docs" / "audit.md"

    if not state_file.is_file() or not audit_file.is_file():
        result = {"additional_context": "AI-DLC state audit hook skipped: required files missing."}
        print(json.dumps(result))
        return 0

    cache_file = Path(tempfile.gettempdir()) / CACHE_FILENAME
    current_hash = sha256_file(state_file)
    previous_hash = cache_file.read_text().strip() if cache_file.is_file() else ""

    if current_hash == previous_hash:
        result = {"additional_context": "AI-DLC state audit hook: no new content change detected."}
        print(json.dumps(result))
        return 0

    cache_file.write_text(current_hash)

    diff_summary = get_diff_summary(repo_root) or "aidlc-state.md modified"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    entry = (
        f"\n## Hook State Audit\n"
        f"**Timestamp**: {timestamp}\n"
        f"**User Input**: \"[Hook-triggered after aidlc-state.md edit]\"\n"
        f"**AI Response**: aidlc-state.md 변경 감지 후 자동 감사 로그를 추가함.\n"
        f"**Context**: {diff_summary}\n\n"
        f"---\n"
    )

    with audit_file.open("a", encoding="utf-8") as f:
        f.write(entry)

    result = {"additional_context": "AI-DLC state audit hook appended audit entry for aidlc-state.md."}
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
