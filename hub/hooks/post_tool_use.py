#!/usr/bin/env python3
"""post_tool_use.py — UniCLI-Hub post-tool hook entry point."""

import json
import sys


def main() -> None:
    try:
        json.loads(sys.stdin.read() or "{}")
    except Exception:
        pass
    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
