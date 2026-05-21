#!/usr/bin/env python3
"""
render_agents.py — Fan-out agents from hub/agents/ to all AI CLI targets.
"""

import sys
import pathlib
import json

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HUB = ROOT / "hub"
AGENTS_SRC = HUB / "agents"

TARGETS = {
    "claude": ROOT / ".claude" / "agents",
    "cursor": ROOT / ".cursor" / "agents",
    "gemini": ROOT / ".gemini" / "agents",
    "codex": ROOT / ".codex" / "prompts",
    "antigravity": ROOT / ".agents" / "agents",
    "antigravity_global": pathlib.Path.home() / ".gemini" / "antigravity-cli" / "agents",
}

SHARED_AGENTS = ["researcher", "codegen", "reviewer"]

MODELS = {
    "claude": {"researcher": "claude-opus-4-7", "codegen": "claude-sonnet-4-6", "reviewer": "claude-opus-4-7"},
    "gemini": {"researcher": "gemini-3-pro-preview", "codegen": "gemini-3-pro-preview", "reviewer": "gemini-3-pro-preview"},
}

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
        try:
            print(f"wrote: {target.relative_to(ROOT)}")
        except ValueError:
            print(f"wrote: {target}")

def render_shared():
    for a in SHARED_AGENTS:
        src = AGENTS_SRC / f"{a}.md"
        if not src.exists(): continue
        body = src.read_text(encoding="utf-8")
        
        # Claude
        fm = f"---\nname: {a}\nmodel: {MODELS['claude'][a]}\n---\n"
        compare_or_write(TARGETS["claude"] / f"{a}.md", fm + body)
        
        # Cursor
        fm = f"---\ndescription: Shared {a} agent\nsource: hub/agents/{a}.md\n---\n"
        compare_or_write(TARGETS["cursor"] / f"{a}.md", fm + body)
        
        # Gemini
        for t in ["gemini"]:
            fm = f"---\nname: {a}\nmodel: {MODELS[t].get(a, 'gemini-3-pro-preview')}\n---\n"
            compare_or_write(TARGETS[t] / f"{a}.md", fm + body)
            
        # Codex
        compare_or_write(TARGETS["codex"] / f"{a}.md", body)

        # Antigravity
        antigravity_content = json.dumps({
            "name": a,
            "description": f"Shared {a} agent",
            "system_prompt": body,
            "enable_mcp_tools": True,
            "enable_write_tools": True
        }, indent=2)
        compare_or_write(TARGETS["antigravity"] / a / "agent.json", antigravity_content)
        compare_or_write(TARGETS["antigravity_global"] / a / "agent.json", antigravity_content)

def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: MODE = arg[2:]

    render_shared()
    # Specialized agents could be handled here by looking for *.json in hub/agents/

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
