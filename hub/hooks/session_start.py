#!/usr/bin/env python3
"""session_start.py — UniCLI-Hub session-start hook.

Per-CLI event names that map to this hook:
  Claude Code : SessionStart  (.claude/settings.json → hooks.SessionStart)
  Cursor      : (no direct equivalent; handled once on first tool use)
  Grok        : SessionStart  (.grok/hooks/unicli-hub.json → hooks.SessionStart)
  Gemini CLI  : (no session-start event as of 2026-05)
  Antigravity : (no hook system as of 2026-05)

Called once when a new AI session begins.
Performs repository update check and target synchronization once per session.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    session_id = None
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict):
            session_id = payload.get("session_id") or payload.get("sessionId")
    except Exception:
        pass

    script_dir = Path(__file__).resolve().parent
    auto_update_path = script_dir / "auto_update.py"
    if auto_update_path.exists():
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "auto_update", auto_update_path
            )
            if spec and spec.loader:
                auto_update = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(auto_update)
                auto_update.check_and_update_session(session_id=session_id)
        except Exception:
            pass


if __name__ == "__main__":
    main()
