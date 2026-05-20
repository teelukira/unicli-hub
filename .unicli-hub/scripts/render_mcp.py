#!/usr/bin/env python3
"""
render_mcp.py — Fan-out MCP configurations from hub/mcp-servers.json to all targets.
"""

import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL = ROOT / "hub" / "mcp-servers.json"

TARGETS = {
    "claude": ROOT / ".mcp.json",
    "cursor": ROOT / ".cursor" / "mcp.json",
    "gemini": ROOT / ".gemini" / "settings.json",
    "agy": ROOT / ".agy" / "settings.json",
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
        print(f"wrote: {target.relative_to(ROOT)}")

def read_json(path: pathlib.Path) -> dict:
    if path.exists():
        with path.open(encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: MODE = arg[2:]

    if not CANONICAL.exists():
        print(f"ERROR: {CANONICAL} not found")
        sys.exit(1)

    src = read_json(CANONICAL)
    servers = src.get("mcpServers", {})

    # 1. Claude & Cursor (Pure JSON)
    mcp_json = json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False) + "\n"
    compare_or_write(TARGETS["claude"], mcp_json)
    compare_or_write(TARGETS["cursor"], mcp_json)

    # 2. Gemini & Agy (Merged JSON)
    for t in ["gemini", "agy"]:
        path = TARGETS[t]
        existing = read_json(path)
        existing["mcpServers"] = servers
        # Ensure 'mcp' allowed list is updated
        if "mcp" not in existing: existing["mcp"] = {}
        existing["mcp"]["allowed"] = list(servers.keys())
        
        compare_or_write(path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n")

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
