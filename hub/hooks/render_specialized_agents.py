#!/usr/bin/env python3
"""
Fan-out specialized agents from .unicli-rules/agents/ to all AI CLI targets.

Each specialized agent has two source files:
  .unicli-rules/agents/{name}.md          — prompt body (canonical)
  .unicli-rules/agents/{name}.kiro.json   — per-CLI metadata (model, tools, resources, etc.)

Outputs:
  .claude/agents/{name}.md          — YAML frontmatter + body
  .kiro/agents/{name}.json          — full Kiro agent JSON (prompt via copied .md)
  .cursor/agents/{name}.md          — Cursor stub (delegates to skill)
  .cursor/skills/{name}/SKILL.md   — full prompt body (mirrors agents/{name}.md)
  .gemini/agents/{name}.md          — Gemini frontmatter + body
  .codex/prompts/{name}.md          — body only

Usage:
  python3 render_specialized_agents.py [--fix|--check]
"""

import json
import sys
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL = ROOT / ".unicli-rules" / "agents"
CLAUDE_DIR = ROOT / ".claude" / "agents"
KIRO_DIR = ROOT / ".kiro" / "agents"
CURSOR_DIR = ROOT / ".cursor" / "agents"
CURSOR_SKILLS_DIR = ROOT / ".cursor" / "skills"
GEMINI_DIR = ROOT / ".gemini" / "agents"
CODEX_DIR = ROOT / ".codex" / "prompts"

SHARED_AGENTS = {"researcher", "codegen", "reviewer"}

# Claude model string normalization: dots → dashes (e.g. claude-opus-4.7 → claude-opus-4-7)
def claude_model(kiro_model: str) -> str:
    return kiro_model.replace(".", "-")

# Gemini model mapping
def gemini_model(kiro_model: str) -> str:
    return "gemini-3.1-pro-preview"

# Kiro tool list → Claude tool names (deduplicated, ordered)
TOOL_MAP = {
    "fs_read": "Read",
    "fs_write": "Write",
    "execute_bash": "Bash",
    "grep": "Grep",
    "glob": "Glob",
    "code": "Bash",
    "web_search": "WebSearch",
    "web_fetch": "WebFetch",
}

def claude_tools(allowed_tools: list) -> str:
    seen = set()
    result = []
    for t in allowed_tools:
        mapped = TOOL_MAP.get(t, t)
        if mapped not in seen:
            result.append(mapped)
            seen.add(mapped)
    return ", ".join(result)


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


def get_agents():
    """Return list of (name, body, kiro_meta) for all specialized agents."""
    agents = []
    for kiro_path in sorted(CANONICAL.glob("*.kiro.json")):
        name = kiro_path.stem.replace(".kiro", "")
        if name in SHARED_AGENTS:
            continue
        md_path = CANONICAL / f"{name}.md"
        if not md_path.exists():
            print(f"WARNING: {md_path} missing, skipping {name}", file=sys.stderr)
            continue
        body = md_path.read_text(encoding="utf-8")
        kiro = json.loads(kiro_path.read_text(encoding="utf-8"))
        agents.append((name, body, kiro))
    return agents


def generate_claude_md(name: str, body: str, kiro: dict) -> str:
    model = claude_model(kiro.get("model", "claude-sonnet-4-6"))
    tools = claude_tools(kiro.get("allowedTools", []))
    desc = kiro.get("description", "")
    fm = textwrap.dedent(f"""\
        ---
        # GENERATED FILE — DO NOT EDIT DIRECTLY. Regenerate: .unicli-rules/sync.sh --fix
        name: {name}
        description: {desc}
        model: {model}
        tools: {tools}
        ---
        """)
    return fm + "\n" + body + "\n"


def generate_kiro_json(name: str, body: str, kiro: dict) -> str:
    # Build output dict preserving all kiro fields, add prompt path
    kiro_out = {}
    kiro_out["name"] = kiro.get("name", name)
    kiro_out["description"] = kiro.get("description", "")
    kiro_out["model"] = kiro.get("model", "claude-sonnet-4.6")
    kiro_out["prompt"] = f"file://prompts/{name}.md"
    kiro_out["tools"] = kiro.get("tools", [])
    kiro_out["allowedTools"] = kiro.get("allowedTools", [])
    if "resources" in kiro:
        kiro_out["resources"] = kiro["resources"]
    if "mcpServers" in kiro:
        kiro_out["mcpServers"] = kiro["mcpServers"]
    if "welcomeMessage" in kiro:
        kiro_out["welcomeMessage"] = kiro["welcomeMessage"]
    if "keyboardShortcut" in kiro:
        kiro_out["keyboardShortcut"] = kiro["keyboardShortcut"]
    return json.dumps(kiro_out, ensure_ascii=False, indent=2) + "\n"


def generate_cursor_agent_skill(name: str, body: str, kiro: dict) -> str:
    desc = kiro.get("description", "")
    fm = textwrap.dedent(f"""\
        ---
        name: {name}
        description: {json.dumps(desc)}
        ---
        """)
    return fm + "\n" + body + "\n"


def generate_cursor_md(name: str, body: str, kiro: dict) -> str:
    desc = kiro.get("description", "")
    fm = textwrap.dedent(f"""\
        ---
        description: {json.dumps(desc)}
        source: .unicli-rules/agents/{name}.md
        skill: .cursor/skills/{name}/SKILL.md
        ---
        """)
    stub = f"""# Cursor agent `{name}` (stub)

You are the **`{name}`** specialized agent.

**Mandatory first step**: Read `.cursor/skills/{name}/SKILL.md` in this repository and follow it end-to-end. That file is the authoritative procedure (synced from `.unicli-rules/agents/{name}.md`).

Role (short): {desc}
"""
    return fm + "\n" + stub + "\n"


def generate_gemini_md(name: str, body: str, kiro: dict) -> str:
    model = gemini_model(kiro.get("model", "claude-sonnet-4.6"))
    desc = kiro.get("description", "")

    # Gemini tool mapping
    GEMINI_TOOL_MAP = {
        "fs_read": "read_file",
        "fs_write": "write_file",
        "execute_bash": "run_shell_command",
        "grep": "grep_search",
        "glob": "glob",
        "code": "run_shell_command",
        "web_search": "google_web_search",
        "web_fetch": "web_fetch",
    }

    allowed = kiro.get("allowedTools", [])
    if not allowed:
        tools_yml = "  - \"*\""
    else:
        g_tools = []
        for t in allowed:
            if t in GEMINI_TOOL_MAP:
                g_tools.append(GEMINI_TOOL_MAP[t])
            elif t.startswith("mcp:"):
                # Map mcp:server:tool to mcp_server_tool
                parts = t.split(":")
                if len(parts) == 3:
                    server = parts[1]
                    # Specific mapping for our repo's MCP server names
                    if server == "atlassian":
                        server = "mcp-atlassian"
                    elif server == "tmf":
                        server = "atom-tmf-kb-mcp"
                    
                    tool = parts[2]
                    if tool == "*":
                        g_tools.append(f"mcp_{server}_*")
                    else:
                        g_tools.append(f"mcp_{server}_{tool}")
                else:
                    g_tools.append("mcp_*")
            elif t.startswith("tmf_kb_"):
                # Explicit mapping for TMF KB tools which are often used without prefix in kiro.json
                g_tools.append(f"mcp_atom-tmf-kb-mcp_{t}")
            else:
                g_tools.append(t)

        # Add 'replace' if 'fs_write' is present
        if "fs_write" in allowed and "replace" not in g_tools:
            g_tools.append("replace")

    unique_tools = sorted(list(set(g_tools)))
    tools_yml = "\n".join([f"  - {t}" for t in unique_tools])

    fm = f"""---
# GENERATED FILE — DO NOT EDIT DIRECTLY. Regenerate: .unicli-rules/sync.sh --fix
name: {name}
description: {desc}
model: {model}
tools:
{tools_yml}
---
"""
    return fm + "\n" + body + "\n"


def generate_codex_md(name: str, body: str, kiro: dict) -> str:
    return body + "\n"


def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg == "--fix":
            MODE = "fix"
        elif arg == "--check":
            MODE = "check"
        else:
            print(f"Unknown arg: {arg}", file=sys.stderr)
            sys.exit(2)

    agents = get_agents()
    if not agents:
        print("No specialized agents found (no *.kiro.json files)", file=sys.stderr)

    for name, body, kiro in agents:
        compare_or_write(CLAUDE_DIR / f"{name}.md", generate_claude_md(name, body, kiro))
        compare_or_write(KIRO_DIR / f"{name}.json", generate_kiro_json(name, body, kiro))
        compare_or_write(
            CURSOR_SKILLS_DIR / name / "SKILL.md",
            generate_cursor_agent_skill(name, body, kiro),
        )
        compare_or_write(CURSOR_DIR / f"{name}.md", generate_cursor_md(name, body, kiro))
        compare_or_write(GEMINI_DIR / f"{name}.md", generate_gemini_md(name, body, kiro))
        compare_or_write(CODEX_DIR / f"{name}.md", generate_codex_md(name, body, kiro))

    if MODE == "check":
        if DRIFT:
            print("✗ specialized agent drift — run: ./.unicli-rules/sync.sh --fix")
            sys.exit(1)
        else:
            print("✓ specialized agents in sync")


if __name__ == "__main__":
    main()
