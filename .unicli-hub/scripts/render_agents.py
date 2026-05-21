#!/usr/bin/env python3
"""
render_agents.py — Fan-out agents from hub/agents/ to all AI CLI targets.
"""

import sys
import pathlib
import json
import re

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
        try:
            print(f"wrote: {target.relative_to(ROOT)}")
        except ValueError:
            print(f"wrote: {target}")

def split_frontmatter(content: str):
    """Split markdown into frontmatter (dict) and body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        fm = {}
        for line in fm_text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip()
        return fm, body
    return {}, content

def render_shared():
    for a in SHARED_AGENTS:
        src = AGENTS_SRC / f"{a}.md"
        if not src.exists(): continue
        raw_content = src.read_text(encoding="utf-8")
        
        fm, body = split_frontmatter(raw_content)
        
        # Claude
        if TARGET_CLI in [None, "claude"]:
            fm_claude = fm.copy()
            fm_claude["name"] = a
            fm_claude["model"] = MODELS["claude"].get(a, "claude-sonnet-4-6")
            
            fm_lines = ["---"]
            for k, v in fm_claude.items(): fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["claude"] / f"{a}.md", "\n".join(fm_lines) + body)
        
        # Cursor
        if TARGET_CLI in [None, "cursor"]:
            fm_cursor = fm.copy()
            fm_cursor["description"] = fm.get("description", f"Shared {a} agent")
            fm_cursor["source"] = f"hub/agents/{a}.md"
            
            fm_lines = ["---"]
            for k, v in fm_cursor.items(): fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["cursor"] / f"{a}.md", "\n".join(fm_lines) + body)
        
        # Gemini
        if TARGET_CLI in [None, "gemini"]:
            fm_gemini = fm.copy()
            fm_gemini["name"] = a
            fm_gemini["description"] = fm.get("description", f"Shared {a} agent")
            fm_gemini["model"] = MODELS["gemini"].get(a, "gemini-3-pro-preview")
            
            fm_lines = ["---"]
            # Ensure name and description are present for Gemini validation
            for k, v in fm_gemini.items(): 
                if k == "aliases": continue # Don't need aliases in final frontmatter
                fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["gemini"] / f"{a}.md", "\n".join(fm_lines) + body)
            
        # Codex
        if TARGET_CLI in [None, "codex"]:
            compare_or_write(TARGETS["codex"] / f"{a}.md", body)

        # Antigravity
        if TARGET_CLI in [None, "antigravity"]:
            antigravity_content = json.dumps({
                "name": a,
                "description": fm.get("description", f"Shared {a} agent"),
                "system_prompt": body,
                "enable_mcp_tools": True,
                "enable_write_tools": True
            }, indent=2)
            compare_or_write(TARGETS["antigravity"] / a / "agent.json", antigravity_content)
            compare_or_write(TARGETS["antigravity_global"] / a / "agent.json", antigravity_content)

def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: 
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = arg.split("=")[1]

    render_shared()
    # Specialized agents could be handled here by looking for *.json in hub/agents/

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
