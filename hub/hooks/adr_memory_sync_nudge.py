#!/usr/bin/env python3
"""adr_memory_sync_nudge.py — PostToolUse hook.

Trigger: PostToolUse on Edit|Write|MultiEdit to files under aidlc-docs/adr/
         (excludes 0000-template.md and README.md).

Behavior:
  Emits an additional_context nudge telling Claude to invoke the
  aidlc-adr-memory-sync skill to update Serena memory. Uses SHA-256 caching
  to skip no-content-change saves (same pattern as state_sync_context.py).

  Exit 0 always — non-blocking. MCP write_memory calls from the skill
  do not re-fire this hook (matcher is Edit|Write, not mcp__serena__*).
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path


CACHE_FILENAME = "tgo-im-adr-memory-sync.sha256"


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


def is_adr_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if "aidlc-docs/adr/" not in normalized:
        return False
    if not normalized.endswith(".md"):
        return False
    filename = Path(normalized).name
    if filename in ("0000-template.md", "README.md"):
        return False
    return True


def sha256_file(file: Path) -> str:
    h = hashlib.sha256()
    h.update(file.read_bytes())
    return h.hexdigest()


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = extract_path(payload)
    if not path or not is_adr_file(path):
        return 0

    adr_file = Path(path)
    if not adr_file.is_file():
        # New file that was just written — no hash check needed
        filename = adr_file.name
        print(json.dumps({
            "additional_context": (
                f"adr-memory-sync: {filename} was added — "
                "invoke the `aidlc-adr-memory-sync` skill to update Serena memory "
                "(catalog.md + per-ADR memo if Accepted status)."
            )
        }))
        return 0

    # SHA-256 cache — skip if file content unchanged
    cache_file = Path(tempfile.gettempdir()) / CACHE_FILENAME
    current_hash = sha256_file(adr_file)

    # Cache is keyed per-file to avoid false skips when different ADRs are edited
    cache_key = f"{adr_file.resolve()}:{current_hash}"
    previous_entry = cache_file.read_text().strip() if cache_file.is_file() else ""
    if previous_entry == cache_key:
        print(json.dumps({"additional_context": "adr-memory-sync: content unchanged — skipped."}))
        return 0
    cache_file.write_text(cache_key)

    filename = adr_file.name
    print(json.dumps({
        "additional_context": (
            f"adr-memory-sync: {filename} changed — "
            "invoke the `aidlc-adr-memory-sync` skill to update Serena memory "
            "(catalog.md + per-ADR memo if Accepted status)."
        )
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
