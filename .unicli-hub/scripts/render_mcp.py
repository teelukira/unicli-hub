#!/usr/bin/env python3
"""
render_mcp.py — Fan-out MCP configurations from hub/mcp-servers.json to all targets.
"""

import json
import sys
import pathlib
import os
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL = ROOT / "hub" / "mcp-servers.json"
ENV_LOCAL = ROOT / ".env.local"

TARGETS = {
    "claude": ROOT / ".mcp.json",
    "cursor": ROOT / ".cursor" / "mcp.json",
    "gemini": ROOT / ".gemini" / "settings.json",
}

MODE = "fix"
DRIFT = False

def load_env(path: pathlib.Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env

def substitute_env(data, env_vars: dict):
    if isinstance(data, dict):
        return {k: substitute_env(v, env_vars) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_env(i, env_vars) for i in data]
    elif isinstance(data, str):
        def replacer(match):
            var_name = match.group(1)
            val = os.environ.get(var_name) or env_vars.get(var_name)
            if val is None:
                print(f"ERROR: Missing environment variable '${var_name}' in .env.local or shell environment.")
                sys.exit(1)
            return val
        return re.sub(r"\${(\w+)}", replacer, data)
    return data

def _display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def compare_or_write(target: pathlib.Path, content: str):
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {_display_path(target)}")
            DRIFT = True
    else:
        target.write_text(content, encoding="utf-8")
        print(f"wrote: {_display_path(target)}")

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

    env_vars = load_env(ENV_LOCAL)
    src = read_json(CANONICAL)
    raw_servers = src.get("mcpServers", {})
    
    # Substitute variables
    servers = substitute_env(raw_servers, env_vars)

    # 1. Claude & Cursor (Pure JSON)
    mcp_json = json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False) + "\n"
    compare_or_write(TARGETS["claude"], mcp_json)
    compare_or_write(TARGETS["cursor"], mcp_json)

    # 2. Gemini (Merged JSON)
    for t in ["gemini"]:
        path = TARGETS[t]
        existing = read_json(path)
        existing["mcpServers"] = servers
        # Ensure 'mcp' allowed list is updated
        if "mcp" not in existing: existing["mcp"] = {}
        existing["mcp"]["allowed"] = list(servers.keys())
        
        compare_or_write(path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n")

    # 3. Antigravity (Distinct JSON with serverUrl)
    ag_servers = {}
    for name, cfg in servers.items():
        ag_cfg = dict(cfg)
        t = ag_cfg.pop("type", None)
        if t == "http":
            if "url" in ag_cfg:
                ag_cfg["serverUrl"] = ag_cfg.pop("url")
            elif "httpUrl" in ag_cfg:
                ag_cfg["serverUrl"] = ag_cfg.pop("httpUrl")
        ag_servers[name] = ag_cfg

    ag_json = json.dumps({"mcpServers": ag_servers}, indent=2, ensure_ascii=False) + "\n"
    compare_or_write(ROOT / ".agents" / "mcp_config.json", ag_json)

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
