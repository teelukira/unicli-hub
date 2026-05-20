#!/usr/bin/env python3
"""render_mcp.py — MCP config renderer for all 5 AI CLIs.

Reads .unicli-rules/common/mcp-servers.json (canonical) and renders
per-CLI MCP config files. Called by sync.sh render_mcp().

Outputs:
  Claude  → .mcp.json                  (JSON: {mcpServers: {...}})
  Cursor  → .cursor/mcp.json           (JSON: {mcpServers: {...}})
  Kiro    → .kiro/settings/mcp.json    (JSON: {mcpServers: {...}})
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
    """Claude / Cursor format: {mcpServers: {...}}"""
    out = {"mcpServers": servers}
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def render_kiro(servers: dict) -> str:
    """Kiro format: {mcpServers: {...}} with 'type' field removed.

    kiro-cli determines server type by presence of 'command' (stdio) vs 'url' (HTTP),
    and does not recognize the 'type' field from the canonical source.
    """
    kiro_servers = {}
    for name, cfg in servers.items():
        k_cfg = dict(cfg)
        k_cfg.pop("type", None)
        kiro_servers[name] = k_cfg
    out = {"mcpServers": kiro_servers}
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

WRITE_GUARD_BLOCK = {
    "matcher": "write_file|replace",
    "hooks": [
        {
            "name": "aidlc-code-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/code_location_guard.py",
        },
        {
            "name": "aidlc-generated-file-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/generated_file_guard.py",
        },
        {
            "name": "aidlc-workflow-transition-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/workflow_transition_guard.py",
        },
    ],
}

SHELL_GUARD_BLOCK = {
    "matcher": "run_shell_command",
    "hooks": [
        {
            "name": "aidlc-shell-sensitive-file-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/shell_sensitive_file_guard.py",
        },
        {
            "name": "aidlc-java-lint-on-commit",
            "type": "command",
            "command": "bash ./.unicli-rules/hooks/java-lint-on-commit.sh",
        },
    ],
}

JIRA_GUARD_BLOCK = {
    "matcher": "mcp_mcp-atlassian_.*",
    "hooks": [
        {
            "name": "aidlc-jira-gate-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/jira_gate_guard.py",
        }
    ],
}

GITLAB_GUARD_BLOCK = {
    "matcher": "mcp_gitlab_create_merge_request",
    "hooks": [
        {
            "name": "aidlc-gitlab-mr-gate-guard",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/gitlab_mr_gate_guard.py",
        }
    ],
}

POST_TOOL_SYNC_BLOCK = {
    "matcher": "write_file|replace",
    "hooks": [
        {
            "name": "aidlc-state-audit",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/state_audit.py",
        },
        {
            "name": "aidlc-plan-checkbox",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/plan_checkbox_tracker.py",
        },
        {
            "name": "aidlc-adr-memory-sync-nudge",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/adr_memory_sync_nudge.py",
        },
        {
            "name": "aidlc-auto-sync",
            "type": "command",
            "command": "python3 ./.unicli-rules/hooks/auto_sync.py",
        },
    ],
}

AFTER_AGENT_BLOCK = {
    "hooks": [
        {
            "name": "ralph-capture-response",
            "type": "command",
            "command": "bash ./.unicli-rules/hooks/ralph-capture-response.sh",
        }
    ]
}

SESSION_END_BLOCK = {
    "hooks": [
        {
            "name": "ralph-stop-hook",
            "type": "command",
            "command": "bash ./.unicli-rules/hooks/ralph-stop-hook.sh",
        }
    ]
}


def ensure_gemini_unicli_hooks(existing: dict) -> None:
    """Ensure all AI-DLC hooks are correctly configured for Gemini CLI."""
    hooks = existing.setdefault("hooks", {})
    
    # 1. Migrate wrong keys (PreToolUse/PostToolUse) back to correct Gemini keys (BeforeTool/AfterTool)
    # Also clean up SessionStart/SessionEnd if they were misconfigured
    for old_key, new_key in [("PreToolUse", "BeforeTool"), ("PostToolUse", "AfterTool")]:
        if old_key in hooks:
            old_val = hooks.pop(old_key)
            if isinstance(old_val, list):
                hooks.setdefault(new_key, []).extend(old_val)

    # 2. Clean up old blocks that contain our canonical hook names
    our_hook_names = {
        "unicli-pre-skill-sync", "aidlc-code-guard", "aidlc-generated-file-guard",
        "aidlc-workflow-transition-guard", "aidlc-shell-sensitive-file-guard",
        "aidlc-java-lint-on-commit", "aidlc-jira-gate-guard", "aidlc-gitlab-mr-gate-guard",
        "aidlc-state-audit", "aidlc-plan-checkbox", "aidlc-adr-memory-sync-nudge",
        "aidlc-auto-sync", "ralph-capture-response", "ralph-stop-hook"
    }
    
    for key in ["BeforeTool", "AfterTool", "AfterAgent", "SessionEnd"]:
        if key in hooks and isinstance(hooks[key], list):
            filtered_blocks = []
            for block in hooks[key]:
                if not isinstance(block, dict):
                    continue
                inner_hooks = block.get("hooks") or []
                contains_our_hook = any(
                    isinstance(h, dict) and h.get("name") in our_hook_names 
                    for h in inner_hooks
                )
                if not contains_our_hook:
                    filtered_blocks.append(block)
            hooks[key] = filtered_blocks

    # 3. Inject canonical blocks
    # BeforeTool
    bt = hooks.setdefault("BeforeTool", [])
    bt.insert(0, PRE_SKILL_READ_BLOCK)
    bt.append(WRITE_GUARD_BLOCK)
    bt.append(SHELL_GUARD_BLOCK)
    bt.append(JIRA_GUARD_BLOCK)
    bt.append(GITLAB_GUARD_BLOCK)

    # AfterTool
    at = hooks.setdefault("AfterTool", [])
    at.append(POST_TOOL_SYNC_BLOCK)

    # Lifecycle hooks
    hooks.setdefault("AfterAgent", []).append(AFTER_AGENT_BLOCK)
    hooks.setdefault("SessionEnd", []).append(SESSION_END_BLOCK)

    # 4. Final deduplication based on block content identity
    for key in ["BeforeTool", "AfterTool", "AfterAgent", "SessionEnd"]:
        if key in hooks and isinstance(hooks[key], list):
            seen_hooks = set()
            unique_blocks = []
            for block in hooks[key]:
                if not isinstance(block, dict):
                    continue
                block_id = json.dumps(block, sort_keys=True)
                if block_id not in seen_hooks:
                    unique_blocks.append(block)
                    seen_hooks.add(block_id)
            hooks[key] = unique_blocks


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
    drift |= write_or_check(ROOT / ".kiro" / "settings" / "mcp.json", render_kiro(servers), mode)

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
