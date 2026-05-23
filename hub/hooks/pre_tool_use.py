#!/usr/bin/env python3
"""pre_tool_use.py — UniCLI-Hub pre-tool hook entry point."""

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    try:
        raw_payload = sys.stdin.read()
        payload = json.loads(raw_payload)
    except Exception:
        print(json.dumps({"permission": "allow"}))
        return

    script_dir = Path(__file__).resolve().parent
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
        encoding="utf-8"
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
