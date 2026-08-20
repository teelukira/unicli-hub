#!/usr/bin/env python3
"""post_tool_use.py — UniCLI-Hub post-tool hook entry point."""

import json
import pathlib
import subprocess
import sys


def main() -> None:
    try:
        json.loads(sys.stdin.read() or "{}")
    except Exception:
        pass

    script_dir = pathlib.Path(__file__).resolve().parent
    lock_sync = script_dir / "lock_sync.py"
    if lock_sync.exists():
        subprocess.run(
            [sys.executable, str(lock_sync)],
            stdout=subprocess.DEVNULL
        )

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
