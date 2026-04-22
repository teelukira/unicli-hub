#!/usr/bin/env python3
"""
Fan-out specialized agents from .unicli-rules/agents/ to all AI CLI targets.

Each specialized agent has two source files:
  .unicli-rules/agents/{name}.md          — prompt body (canonical)
  .unicli-rules/agents/{name}.kiro.json   — per-CLI metadata (model, tools, resources, etc.)

Outputs:
  .claude/agents/{name}.md          — YAML frontmatter + body
  .kiro/agents/{name}.json          — full Kiro agent JSON (prompt via copied .md)
  .cursor/agents/{name}.md          — Cursor frontmatter + body
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
GEMINI_DIR = ROOT / ".gemini" / "agents"
CODEX_DIR = ROOT / ".codex" / "prompts"

SHARED_AGENTS = {"researcher", "codegen", "reviewer"}

def claude_model(kiro_model: str) -> str:
    return kiro_model.replace(".", "-")

def gemini_model(kiro_model: str) -> str:
    return "gemini-3-pro-preview"

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


def generate_cursor_md(name: str, body: str, kiro: dict) -> str:
    desc = kiro.get("description", "")
    fm = textwrap.dedent(f"""\
        ---
        description: {desc}
        source: .unicli-rules/agents/{name}.md
        ---
        """)
    return fm + "\n" + body + "\n"


def generate_gemini_md(name: str, body: str, kiro: dict) -> str:
    model = gemini_model(kiro.get("model", "claude-sonnet-4.6"))
    desc = kiro.get("description", "")
    fm = textwrap.dedent(f"""\
        ---
        name: {name}
        description: {desc}
        model: {model}
        ---
        """)
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
