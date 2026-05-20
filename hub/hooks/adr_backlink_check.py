#!/usr/bin/env python3
"""
adr_backlink_check.py — PostToolUse hook (Phase 5 spec, not yet wired).

Trigger: PostToolUse on Edit/Write to files matching `aidlc-docs/construction/*/INDEX.md`.

Behavior:
  - Reads the changed INDEX.md.
  - Verifies the presence of a `**Relates-To-ADR**:` line in the first 30 lines
    (header region).
  - Exits 0 on PASS; emits a warning + exit 1 on missing backlink (blocking when
    activated as a blocking hook).

Activation (Phase 6):
  - Symlink or copy to `.claude/hooks/adr_backlink_check.py`.
  - Add to `.claude/settings.local.json` PostToolUse matchers for
    `Edit|Write|MultiEdit` on `aidlc-docs/construction/*/INDEX.md`.
  - Enable governance extension in `aidlc-docs/aidlc-state.md`.

Status (2026-05-12): spec-only. NOT wired into any settings. Calling it directly
on any file is safe — it only reads and prints.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BACKLINK_HEADER_LINES = 30
BACKLINK_PATTERN = re.compile(r"^\*\*Relates-To-ADR\*\*:\s*", re.MULTILINE)
TARGET_PATTERN = re.compile(r"aidlc-docs/construction/[^/]+/INDEX\.md$")


def is_target(path: str) -> bool:
    return bool(TARGET_PATTERN.search(path.replace("\\", "/")))


def has_backlink(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as fh:
            head = "".join(next(fh, "") for _ in range(BACKLINK_HEADER_LINES))
    except OSError:
        return False
    return bool(BACKLINK_PATTERN.search(head))


def main() -> int:
    # Claude Code PostToolUse hook payload is JSON on stdin; fallback to argv for CLI use.
    payload: dict = {}
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

    file_paths: list[str] = []
    if "tool_input" in payload:
        ti = payload["tool_input"]
        if isinstance(ti, dict):
            for key in ("file_path", "path", "filePath"):
                val = ti.get(key)
                if isinstance(val, str):
                    file_paths.append(val)
    if not file_paths and len(sys.argv) > 1:
        file_paths = list(sys.argv[1:])

    targets = [p for p in file_paths if is_target(p)]
    if not targets:
        return 0  # nothing relevant

    missing: list[str] = []
    for raw in targets:
        path = Path(raw)
        if not path.exists():
            continue
        if not has_backlink(path):
            missing.append(str(path))

    if missing:
        sys.stderr.write(
            "\n[adr_backlink_check] BLOCKING: unit INDEX.md missing **Relates-To-ADR** backlink:\n"
        )
        for m in missing:
            sys.stderr.write(f"  - {m}\n")
        sys.stderr.write(
            "\nAdd a line near the top, for example:\n"
            "  **Relates-To-ADR**: [0005](../../adr/cross-cutting/0005-hexagonal-4-module-layout.md), [0019](../../adr/microservices/0019-ipam-service-domain-scope.md)\n"
            "\nSee .unicli-rules/common/adr-conventions.md and aidlc-docs-unit-conventions.md.\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
