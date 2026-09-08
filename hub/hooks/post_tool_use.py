#!/usr/bin/env python3
"""post_tool_use.py — UniCLI-Hub post-tool hook entry point."""

import json
import sys

from hook_output import allow_doc, emit


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    # PostToolUse cannot decide anything — the tool already ran. Claude Code
    # accepts only hookEventName/additionalContext here, so it gets silence.
    emit(allow_doc(payload))


if __name__ == "__main__":
    main()
