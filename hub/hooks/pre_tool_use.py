#!/usr/bin/env python3
"""pre_tool_use.py — UniCLI-Hub pre-tool hook entry point.

1. Ensures repository is updated and synced once per session.
2. Enforces generated_file_guard to block direct modifications to derived files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def ensure_session_updated(payload: dict, script_dir: Path) -> None:
    try:
        session_id = payload.get("session_id") or payload.get("sessionId")
        auto_update_path = script_dir / "auto_update.py"
        if auto_update_path.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "auto_update", auto_update_path
            )
            if spec and spec.loader:
                auto_update = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(auto_update)
                auto_update.check_and_update_session(session_id=session_id)
    except Exception:
        # Never break tool execution on auto-update failure (fail-open)
        pass


def main() -> None:
    raw_payload = ""
    try:
        raw_payload = sys.stdin.read()
        payload = json.loads(raw_payload) if raw_payload.strip() else {}
    except Exception:
        payload = {}

    script_dir = Path(__file__).resolve().parent

    # 1. Once per session update check
    if isinstance(payload, dict):
        ensure_session_updated(payload, script_dir)

    # 2. Run generated_file_guard
    guard = script_dir / "generated_file_guard.py"
    if not guard.exists():
        print(json.dumps({"permission": "allow"}))
        return

    proc = subprocess.Popen(
        [sys.executable, str(guard)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    stdout, stderr = proc.communicate(input=raw_payload)

    # Pass through stderr (for nudges/logs)
    if stderr:
        sys.stderr.write(stderr)
        sys.stderr.flush()

    if stdout.strip():
        sys.stdout.write(stdout)
    else:
        print(json.dumps({"permission": "allow"}))

    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
