#!/usr/bin/env python3
"""
render_hooks.py — Fan-out hook configurations from hub/ to all AI CLI targets.
"""

import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HUB = ROOT / "hub"

# Canonical hook sources (SSOT)
CLAUDE_HOOKS_SRC = HUB / "claude-hooks.json"
CURSOR_HOOKS_SRC = HUB / "cursor-hooks.json"

# Targets
CLAUDE_SETTINGS = ROOT / ".claude" / "settings.json"
CURSOR_HOOKS = ROOT / ".cursor" / "hooks.json"
ANTIGRAVITY_SETTINGS = ROOT / ".agents" / "settings.json"
GEMINI_SETTINGS = ROOT / ".gemini" / "settings.json"

MODE = "fix"
TARGET_CLI = None
DRIFT = False


def compare_or_write(target: pathlib.Path, content: str):
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {target.relative_to(ROOT)}")
            DRIFT = True
    else:
        target.write_text(content, encoding="utf-8")
        print(f"wrote: {target.relative_to(ROOT)}")


def render_claude():
    if not CLAUDE_HOOKS_SRC.exists():
        return
    content = CLAUDE_HOOKS_SRC.read_text(encoding="utf-8")
    compare_or_write(CLAUDE_SETTINGS, content)


def render_cursor():
    if not CURSOR_HOOKS_SRC.exists():
        return
    content = CURSOR_HOOKS_SRC.read_text(encoding="utf-8")
    compare_or_write(CURSOR_HOOKS, content)


def render_agy_hooks() -> str:
    if not CLAUDE_HOOKS_SRC.exists():
        return '{"hooks": {}}\n'
    raw_content = CLAUDE_HOOKS_SRC.read_text(encoding="utf-8")
    try:
        data = json.loads(raw_content)
        hooks = data.get("hooks", {})
        agy_hooks = {}

        event_map = {
            "PreToolUse": "BeforeTool",
            "PostToolUse": "AfterTool",
            "SessionStart": "SessionStart",
            # Stop is intentionally omitted: agy/gemini settings reject it.
        }

        for source_event, target_event in event_map.items():
            if source_event in hooks:
                agy_hooks[target_event] = hooks[source_event]

        return json.dumps({"hooks": agy_hooks}, indent=2) + "\n"
    except Exception:
        return '{"hooks": {}}\n'


def render_antigravity():
    compare_or_write(ANTIGRAVITY_SETTINGS, render_agy_hooks())


def render_gemini():
    compare_or_write(GEMINI_SETTINGS, render_agy_hooks())


def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]:
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = arg.split("=")[1]

    if TARGET_CLI in [None, "claude"]:
        render_claude()
    if TARGET_CLI in [None, "cursor"]:
        render_cursor()
    if TARGET_CLI in [None, "antigravity", "agy"]:
        render_antigravity()
    if TARGET_CLI in [None, "gemini"]:
        render_gemini()

    if MODE == "check" and DRIFT:
        sys.exit(1)


if __name__ == "__main__":
    main()
