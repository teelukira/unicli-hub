#!/usr/bin/env python3
"""aidlc_unified_hook.py — Unified Hook Dispatcher for AI-DLC.

Single entry point for all AI CLI hooks (Claude, Cursor, Gemini, Kiro, Codex).
Delegates guard/gate logic to hook_common.py; keeps audit/tracker logic here.

Usage:
  python3 aidlc_unified_hook.py --phase [before|after] --tool <tool_name>
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_FILE = REPO_ROOT / "aidlc-docs" / "audit.md"
STATE_FILE = REPO_ROOT / "aidlc-docs" / "aidlc-state.md"
MAX_AUDIT_SIZE = 1024 * 1024  # 1 MB


def _load_common():
    path = Path(__file__).parent / "hook_common.py"
    spec = importlib.util.spec_from_file_location("aidlc_hook_common", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Audit helpers (local — no hook_common dependency needed)
# ---------------------------------------------------------------------------

def _rotate_audit() -> None:
    if not AUDIT_FILE.exists() or AUDIT_FILE.stat().st_size < MAX_AUDIT_SIZE:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = AUDIT_FILE.with_name(f"audit.{ts}.md")
    try:
        AUDIT_FILE.rename(archive)
        AUDIT_FILE.write_text(
            f"# AI-DLC Audit Log\n\nRotated from previous log at {ts}.\n\n---\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _append_audit(entry: str) -> None:
    _rotate_audit()
    try:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def main() -> int:
    phase = ""
    tool = ""
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--phase" and i + 1 < len(sys.argv):
            phase = sys.argv[i + 1]
        if sys.argv[i] == "--tool" and i + 1 < len(sys.argv):
            tool = sys.argv[i + 1]

    hc = _load_common()

    raw = hc.read_stdin_payload()
    if not raw.strip():
        return hc.allow()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return hc.allow()

    if phase == "before":
        return _handle_before(tool, payload, hc)
    if phase == "after":
        return _handle_after(tool, payload, hc)
    
    # AfterAgent or SessionEnd
    return hc.allow()


def _handle_before(tool: str, payload: dict, hc) -> int:
    path = hc.extract_path(payload)

    # --- Skill sync (debounced read) ---
    if hc.is_read_tool(tool) and hc.is_skill_sync_path(path):
        hc.run_sync()
        return hc.allow()

    # --- File-mutation guards ---
    if hc.is_edit_tool(tool):
        err = hc.check_code_location(path)
        if err:
            return hc.block(err)
        err = hc.check_generated_file(path)
        if err:
            return hc.block(err)
        err = hc.check_workflow_transition(payload)
        if err:
            return hc.block(err)
        err = hc.check_adr_backlink(path)
        if err:
            return hc.block(err)
        nudge = hc.adr_memory_nudge(path)
        if nudge:
            print(nudge, file=sys.stderr)

    # --- Shell guard ---
    if hc.is_shell_tool(tool):
        err = hc.check_shell_guard(payload)
        if err:
            return hc.block(err)

    # --- MCP gates ---
    err = hc.check_jira_gate(payload, tool)
    if err:
        return hc.block(err)
    err = hc.check_gitlab_gate(payload, tool)
    if err:
        return hc.block(err)

    return hc.allow()


def _handle_after(tool: str, payload: dict, hc) -> int:
    path = hc.extract_path(payload)

    # --- State audit + context sync on aidlc-state.md writes ---
    if hc.is_edit_tool(tool) and hc.normalize_path(path) == hc.STATE_FILE:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _append_audit(
            f"\n## Unified Hook Audit\n**Timestamp**: {ts}\n"
            f"**Context**: aidlc-state.md modified via {tool}\n\n---\n"
        )
        try:
            sc_path = Path(__file__).parent / "state_sync_context.py"
            spec = importlib.util.spec_from_file_location("state_sync_context", sc_path)
            sc = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(sc)
            sc.sync_if_state_changed(path)
        except Exception:
            pass

    # --- Plan checkbox tracker ---
    if "plan.md" in path:
        try:
            content = Path(path).read_text(encoding="utf-8")
            done = len(re.findall(r"- \[x\]", content, re.IGNORECASE))
            todo = len(re.findall(r"- \[ \]", content))
            if (done + todo) > 0:
                print(f"\n[plan-tracker] {done}/{done + todo} steps complete.", file=sys.stderr)
        except OSError:
            pass

    # --- Auto sync after rules/skill edits ---
    norm = path.replace("\\", "/")
    if hc.is_skill_sync_path(path) or "/hub/" in norm or norm.startswith("hub/"):
        hc.run_sync()

    return hc.allow()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print(
            json.dumps({
                "permission": "deny",
                "user_message": "Unified hook crash: " + traceback.format_exc(limit=1),
                "agent_message": "aidlc_unified_hook.py exception — see user_message",
            })
        )
        sys.exit(1)
