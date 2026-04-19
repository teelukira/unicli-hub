#!/usr/bin/env python3
"""render_mcp.py — MCP config renderer for all 5 AI CLIs.

Reads .unicli-rules/common/mcp-servers.json (canonical) and renders
per-CLI MCP config files. Called by sync.sh render_mcp().

Outputs:
  Claude  → .mcp.json                  (JSON: {mcpServers: {...}})
  Cursor  → .cursor/mcp.json           (JSON: {mcpServers: {...}})
  Kiro    → .kiro/mcp.json             (JSON: {mcpServers: {...}})
  Gemini  → .gemini/settings.json      (JSON merge: preserve existing hooks)
  Codex   → .codex/config.toml         (TOML append: [[mcpServers]] array)

Usage:
  python3 render_mcp.py --fix   [default]
  python3 render_mcp.py --check  (exit 1 if any output is out of sync)
"""

from __future__ import annotations

import json
import sys
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT = (SCRIPT_DIR / "../..").resolve()          # unicli-hub root
CANONICAL = SCRIPT_DIR.parent / "common" / "mcp-servers.json"


def load_canonical() -> dict:
    with CANONICAL.open(encoding="utf-8") as f:
        data = json.load(f)
    servers = {k: v for k, v in data["mcpServers"].items() if not k.startswith("_")}
    return servers


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_json(path: Path) -> dict:
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_or_check(path: Path, content: str, mode: str) -> bool:
    """Return True if drift detected (check mode) or write was performed (fix mode)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "check":
        if not path.exists():
            print(f"DRIFT (missing): {path.relative_to(ROOT)}")
            return True
        existing = path.read_text(encoding="utf-8")
        if existing != content:
            print(f"DRIFT: {path.relative_to(ROOT)}")
            return True
        return False
    else:
        path.write_text(content, encoding="utf-8")
        print(f"wrote: {path.relative_to(ROOT)}")
        return False


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_json_mcp(servers: dict) -> str:
    """Claude / Cursor / Kiro format: {mcpServers: {...}}"""
    out = {"mcpServers": servers}
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


PRE_SKILL_READ_BLOCK = {
    "matcher": "read_file",
    "hooks": [
        {
            "name": "unicli-pre-skill-sync",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/pre_skill_sync.py",
        }
    ],
}


def _gemini_has_pre_skill_read(before_tool: object) -> bool:
    if not isinstance(before_tool, list):
        return False
    for block in before_tool:
        if not isinstance(block, dict):
            continue
        if block.get("matcher") != "read_file":
            continue
        for h in block.get("hooks") or []:
            if isinstance(h, dict) and h.get("name") == "unicli-pre-skill-sync":
                return True
    return False


def ensure_gemini_unicli_hooks(existing: dict) -> None:
    """Ensure read_file runs pre_skill_sync when missing (e.g. fresh settings.json)."""
    hooks = existing.setdefault("hooks", {})
    before = hooks.get("BeforeTool")
    if not isinstance(before, list):
        before = []
    if not _gemini_has_pre_skill_read(before):
        hooks["BeforeTool"] = [PRE_SKILL_READ_BLOCK] + before


def render_gemini(servers: dict) -> str:
    """Merge mcpServers into .gemini/settings.json, preserving other keys."""
    settings_path = ROOT / ".gemini" / "settings.json"
    existing = read_json(settings_path)

    gemini_servers = {}
    for name, cfg in servers.items():
        # Copy to avoid mutating the original
        g_cfg = dict(cfg)
        t = g_cfg.pop("type", None)
        if t == "http" and "url" in g_cfg:
            g_cfg["httpUrl"] = g_cfg.pop("url")
        gemini_servers[name] = g_cfg

    existing["mcpServers"] = gemini_servers

    # Explicitly allow these servers to ensure they are visible
    if "mcp" not in existing:
        existing["mcp"] = {}
    existing["mcp"]["allowed"] = list(gemini_servers.keys())

    ensure_gemini_unicli_hooks(existing)

    return json.dumps(existing, indent=2, ensure_ascii=False) + "\n"


def render_codex_toml(servers: dict) -> str:
    """Generate TOML [[mcpServers]] array for Codex config.toml.

    Codex CLI uses TOML array-of-tables for MCP servers.
    HTTP-type servers are skipped (Codex only supports stdio).
    See: https://github.com/openai/codex/blob/main/docs/config.md
    """
    lines: list[str] = []
    for name, cfg in servers.items():
        if cfg.get("type") == "http":
            continue  # Codex stdio only
        lines.append("[[mcpServers]]")
        lines.append(f'name = "{name}"')
        cmd = cfg.get("command", "")
        if cmd:
            lines.append(f'command = "{cmd}"')
        args = cfg.get("args", [])
        if args:
            args_toml = ", ".join(f'"{a}"' for a in args)
            lines.append(f"args = [{args_toml}]")
        env = cfg.get("env", {})
        if env:
            lines.append("[mcpServers.env]  # last table — must follow scalar keys")
            for k, v in env.items():
                lines.append(f'{k} = "{v}"')
        lines.append("")
    return "\n".join(lines)


def merge_codex_toml(existing_toml: str, mcp_toml: str) -> str:
    """Replace [[mcpServers]] block in existing config.toml, preserving other settings."""
    import re
    # Strip everything from the generated MCP comment onwards (idempotent anchor)
    anchor = "# MCP servers — generated by render_mcp.py, do not edit directly"
    if anchor in existing_toml:
        base = existing_toml[:existing_toml.index(anchor)].rstrip()
    else:
        base = existing_toml.rstrip()
    if not mcp_toml.strip():
        return base + "\n"
    return base + "\n\n" + anchor + "\n" + mcp_toml


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    mode = "fix"
    for arg in sys.argv[1:]:
        if arg == "--check":
            mode = "check"
        elif arg == "--fix":
            mode = "fix"
        else:
            print(f"Unknown arg: {arg}", file=sys.stderr)
            return 2

    servers = load_canonical()
    drift = False

    # Claude
    drift |= write_or_check(ROOT / ".mcp.json", render_json_mcp(servers), mode)

    # Cursor
    drift |= write_or_check(ROOT / ".cursor" / "mcp.json", render_json_mcp(servers), mode)

    # Kiro
    drift |= write_or_check(ROOT / ".kiro" / "mcp.json", render_json_mcp(servers), mode)

    # Gemini (merge)
    drift |= write_or_check(ROOT / ".gemini" / "settings.json", render_gemini(servers), mode)

    # Codex (merge into config.toml)
    codex_toml_path = ROOT / ".codex" / "config.toml"
    existing_toml = codex_toml_path.read_text(encoding="utf-8") if codex_toml_path.exists() else ""
    mcp_toml = render_codex_toml(servers)
    merged_toml = merge_codex_toml(existing_toml, mcp_toml)
    drift |= write_or_check(codex_toml_path, merged_toml, mode)

    if mode == "check" and drift:
        print("✗ MCP drift detected — run: ./.unicli-rules/sync.sh --fix")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
