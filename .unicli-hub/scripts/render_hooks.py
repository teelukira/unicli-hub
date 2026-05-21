#!/usr/bin/env python3
"""
render_hooks.py — Fan-out hook configurations from hub/ to all AI CLI targets.
"""

import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HUB = ROOT / "hub"

# Canonical hook sources
CLAUDE_HOOKS_SRC = HUB / "claude-hooks.json"
CURSOR_HOOKS_SRC = HUB / "cursor-hooks.json"

# Targets
CLAUDE_SETTINGS = ROOT / ".claude" / "settings.json"
CURSOR_HOOKS = ROOT / ".cursor" / "hooks.json"
GEMINI_SETTINGS = ROOT / ".gemini" / "settings.json"

MODE = "fix"
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

def read_json(path: pathlib.Path) -> dict:
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {}

def render_claude():
    if not CLAUDE_HOOKS_SRC.exists(): return
    content = CLAUDE_HOOKS_SRC.read_text(encoding="utf-8")
    # Replace old path placeholder with new framework path if needed
    content = content.replace("./.unicli-rules/hooks/", "./hub/hooks/")
    compare_or_write(CLAUDE_SETTINGS, content)

def render_cursor():
    if not CURSOR_HOOKS_SRC.exists(): return
    content = CURSOR_HOOKS_SRC.read_text(encoding="utf-8")
    content = content.replace("./.unicli-rules/hooks/", "./hub/hooks/")
    compare_or_write(CURSOR_HOOKS, content)

def render_gemini_like(target_path: pathlib.Path):
    existing = read_json(target_path)
    # Basic hooks for Gemini-like CLIs
    hooks = existing.setdefault("hooks", {})
    
    # Pre-skill sync hook
    bt = hooks.setdefault("BeforeTool", [])
    skill_sync = {
        "name": "unicli-pre-skill-sync",
        "type": "command",
        "command": "python3 hub/hooks/pre_skill_sync.py"
    }
    if skill_sync not in bt: bt.insert(0, skill_sync)

    # Auto sync hook
    at = hooks.setdefault("AfterTool", [])
    auto_sync = {
        "name": "unicli-auto-sync",
        "type": "command",
        "command": "python3 hub/hooks/auto_sync.py"
    }
    if auto_sync not in at: at.append(auto_sync)

    compare_or_write(target_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n")

def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: MODE = arg[2:]

    render_claude()
    render_cursor()
    render_gemini_like(GEMINI_SETTINGS)

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
