#!/usr/bin/env python3
"""state_sync_context.py — PostToolUse hook.

When aidlc-docs/aidlc-state.md is modified, syncs the unit 상태 column in
.unicli-rules/project-context.md from the "Phase 1 완료 현황" table.

Design intent — only TRANSITIONS are synced:
  - ⏸ 대기 or 🔄 진행중  →  ✅ 완료 (derived from state + TMF + note)
  - Both sides already ✅  →  SKIP (project-context.md may have richer QA detail
    than state carries; do not overwrite with a thinner derived string)
  - ✅  →  ⏸/🔄 (regression) → update

After updating project-context.md, invokes sync.sh --fix so every derived
CLI directory (CLAUDE.md, AGENTS.md, .gemini/, .cursor/, .kiro/, .codex/)
stays in sync. No sync.sh call when nothing changes.

SHA-256 cache avoids redundant re-runs on no-content-change saves.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


STATE_FILE_SUFFIX = "aidlc-docs/aidlc-state.md"
CACHE_FILENAME = "tgo-im-aidlc-state-ctx.sha256"


# ---------------------------------------------------------------------------
# Payload extraction (multi-CLI schema support)
# ---------------------------------------------------------------------------

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
    return path.replace("\\", "/").endswith(STATE_FILE_SUFFIX)


def sha256_file(file: Path) -> str:
    h = hashlib.sha256()
    h.update(file.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Parse aidlc-state.md Phase 1 완료 현황 table
# ---------------------------------------------------------------------------

def parse_state_table(content: str) -> dict[str, dict[str, str]]:
    """Return {unit_id: {status, tmf, note}} from Phase 1 완료 현황 table."""
    units: dict[str, dict[str, str]] = {}
    in_table = False

    for line in content.splitlines():
        if "Phase 1 완료 현황" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if not line.strip():
            continue
        if not line.startswith("|"):
            break  # table ended

        cols = [c.strip() for c in line.split("|")]
        cols = [c for c in cols if c != ""]  # strip leading/trailing empty

        if not cols or cols[0].startswith("-") or cols[0] == "Unit":
            continue  # header / separator rows

        unit_id = cols[0]
        if not unit_id or not re.match(r"U\d", unit_id):
            continue

        units[unit_id] = {
            "status": cols[2] if len(cols) > 2 else "",
            "tmf":    cols[3] if len(cols) > 3 else "",
            "note":   cols[4] if len(cols) > 4 else "",
        }

    return units


# ---------------------------------------------------------------------------
# Derive display status for project-context.md
# ---------------------------------------------------------------------------

def _qa_from_note(note: str) -> str:
    m = re.search(r"QA PASS(?:\s+\d+/\d+)?", note)
    return m.group(0) if m else ""


def _nc_count_from_note(note: str) -> str:
    m = re.search(r"(\d+)\s+NC", note)
    return m.group(1) if m else "?"


def derive_display_status(status: str, tmf: str, note: str) -> str:
    """Derive the combined status cell value for project-context.md."""
    # Already carries parenthesised detail (e.g. "✅ 완료 (QA PASS, TMF PASS)")
    if "(" in status:
        return status

    base = status.strip()

    if not base.startswith("✅"):
        return base  # ⏸ 대기 / 🔄 진행중 / etc. — use verbatim

    # ---- ✅ 완료 — build suffix -----------------------------------------
    qa_str = _qa_from_note(note)
    tmf_up = tmf.strip().upper()

    if tmf_up in ("", "-", "N/A"):
        tmf_suffix = ""
    elif tmf_up == "PASS":
        tmf_suffix = "TMF PASS"
    elif "FAIL" in tmf_up:
        nc = _nc_count_from_note(note)
        tmf_suffix = f"TMF FAIL — {nc} NC waived"
    elif "CONDITIONAL" in tmf_up:
        tmf_suffix = "TMF CONDITIONAL PASS"
    else:
        tmf_suffix = f"TMF {tmf.strip()}"

    parts = [p for p in [qa_str, tmf_suffix] if p]
    return f"✅ 완료 ({', '.join(parts)})" if parts else "✅ 완료"


# ---------------------------------------------------------------------------
# Read current statuses from project-context.md Quick Reference table
# ---------------------------------------------------------------------------

_STATUS_CELL_RE = re.compile(
    r"^(\|\s*(?P<unit>U[\w-]+)\s*\|(?:[^|]*\|){3})(?P<status>[^|]+)(\|)",
    re.MULTILINE,
)


def parse_context_statuses(content: str) -> dict[str, str]:
    """Return {unit_id: current_status} from Quick Reference table."""
    units: dict[str, str] = {}
    in_table = False

    for line in content.splitlines():
        if "Quick Reference" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if line.strip() == "" or not line.startswith("|"):
            if in_table and not line.startswith("|"):
                break
            continue
        cols = [c.strip() for c in line.split("|")]
        cols = [c for c in cols if c != ""]
        if not cols or cols[0].startswith("-") or cols[0] == "Unit":
            continue
        unit_id = cols[0]
        if not re.match(r"U[\w-]+", unit_id):
            continue
        # Status is the last column (col 4, 0-indexed)
        units[unit_id] = cols[4] if len(cols) > 4 else ""

    return units


# ---------------------------------------------------------------------------
# Patch a single status cell in project-context.md
# ---------------------------------------------------------------------------

def patch_status(content: str, unit_id: str, new_status: str) -> str:
    """Replace the 상태 cell for unit_id in the Quick Reference table."""
    # Pattern: | U05 | <name col> | <coverage col> | <human col> | OLD_STATUS |
    pattern = (
        r"(\|\s*" + re.escape(unit_id) + r"\s*\|"
        r"(?:[^|]*\|){3})"    # name + coverage + human cols
        r"([^|]+)"            # existing status cell
        r"(\|)"
    )
    replacement = rf"\g<1> {new_status} \g<3>"
    new_content, n = re.subn(pattern, replacement, content)
    return new_content if n else content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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
    state_file  = repo_root / "aidlc-docs" / "aidlc-state.md"
    context_file = repo_root / ".unicli-rules" / "project-context.md"
    sync_script  = repo_root / ".unicli-rules" / "sync.sh"

    if not state_file.is_file() or not context_file.is_file():
        return 0

    # SHA-256 cache — skip if state file content unchanged
    cache_file = Path(tempfile.gettempdir()) / CACHE_FILENAME
    current_hash = sha256_file(state_file)
    previous_hash = cache_file.read_text().strip() if cache_file.is_file() else ""
    if current_hash == previous_hash:
        print(json.dumps({"additional_context": "state-sync-context: state unchanged — skipped."}))
        return 0
    cache_file.write_text(current_hash)

    # Parse both files
    state_units   = parse_state_table(state_file.read_text(encoding="utf-8"))
    context_text  = context_file.read_text(encoding="utf-8")
    context_statuses = parse_context_statuses(context_text)

    if not state_units:
        print(json.dumps({"additional_context": "state-sync-context: no units found in state table."}))
        return 0

    # Determine which units need updating
    updated: list[str] = []
    new_text = context_text

    for unit_id, info in state_units.items():
        new_status = derive_display_status(info["status"], info["tmf"], info["note"])
        current_status = context_statuses.get(unit_id, "")

        current_complete = "✅" in current_status
        new_complete     = "✅" in new_status

        # Skip if both sides already show ✅ — preserve richer manual detail
        if current_complete and new_complete:
            continue

        if current_status.strip() == new_status.strip():
            continue  # already identical

        new_text = patch_status(new_text, unit_id, new_status)
        updated.append(unit_id)

    if not updated:
        print(json.dumps({"additional_context": "state-sync-context: no status transitions detected."}))
        return 0

    context_file.write_text(new_text, encoding="utf-8")

    # Propagate to derived files via sync.sh
    if sync_script.is_file() and os.access(sync_script, os.X_OK):
        print(f"state-sync-context: updated {updated} — running sync.sh --fix")
        subprocess.run([str(sync_script), "--fix"], cwd=str(repo_root), check=False)
    else:
        print(f"state-sync-context: updated {updated} but sync.sh not found; derived files may drift.",
              file=sys.stderr)

    print(json.dumps({
        "additional_context": f"state-sync-context: synced {len(updated)} unit(s) to project-context.md: {updated}"
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
