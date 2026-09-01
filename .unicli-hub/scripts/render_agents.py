#!/usr/bin/env python3
"""
render_agents.py — Fan-out agents from hub/agents/ to all AI CLI targets.
"""

import sys
import pathlib
import json
import re

_SCRIPTS = pathlib.Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from cli_names import canonical_cli

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HUB = ROOT / "hub"
REGISTRY_DIR = HUB / "registry"
FANOUT_REGISTRY = REGISTRY_DIR / "fanout.json"
AGENT_PROFILES_REGISTRY = REGISTRY_DIR / "agent-profiles.json"

def resolve_path(path_value: str) -> pathlib.Path:
    path = pathlib.Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path

def read_json(path: pathlib.Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)

FANOUT = read_json(FANOUT_REGISTRY).get("agents", {})
AGENTS_SRC = resolve_path(FANOUT.get("source", "hub/agents"))
TARGETS = {
    name: resolve_path(path)
    for name, path in FANOUT.get("targets", {
        "claude": ".claude/agents",
        "cursor": ".cursor/agents",
        "codex": ".codex/prompts",
        "grok": ".grok/agents",
    }).items()
}

AGENT_PROFILES = read_json(AGENT_PROFILES_REGISTRY)
CLAUDE_AGENT_PROFILES = AGENT_PROFILES.get("claude", {})
DEFAULT_CLAUDE_AGENT_PROFILE = AGENT_PROFILES.get("defaults", {}).get("claude", {
    "model": "sonnet",
})
CODEX_AGENT_PROFILES = AGENT_PROFILES.get("codex", {})
DEFAULT_CODEX_AGENT_PROFILE = AGENT_PROFILES.get("defaults", {}).get("codex", {
    "model": "gpt-5.6",
    "reasoning_effort": "medium",
})
CURSOR_AGENT_PROFILES = AGENT_PROFILES.get("cursor", {})
DEFAULT_CURSOR_AGENT_PROFILE = AGENT_PROFILES.get("defaults", {}).get("cursor", {
    "model": "inherit",
    "readonly": False,
    "is_background": False,
})
GROK_AGENT_PROFILES = AGENT_PROFILES.get("grok", {})
DEFAULT_GROK_AGENT_PROFILE = AGENT_PROFILES.get("defaults", {}).get("grok", {
    "model": "inherit",
    "prompt_mode": "full",
    "permission_mode": "default",
    "agents_md": True,
})

CURSOR_FRONTMATTER_KEYS = ("name", "description", "model", "readonly", "is_background")
GROK_FRONTMATTER_KEYS = ("name", "description", "prompt_mode", "model", "permission_mode", "agents_md")

MODE = "fix"
TARGET_CLI = None
DRIFT = False
PRODUCED_AGENTS: set = set()

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

def parse_frontmatter_fields(fm_text: str) -> dict:
    """Parse simple YAML frontmatter, including folded (`>`) and literal (`|`) scalars."""
    fm = {}
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            i += 1
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val in (">", ">-", "|", "|-"):
            folded = val in (">", ">-")
            block = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in " \t"):
                block.append(lines[i].strip())
                i += 1
            text = " ".join(part for part in block if part) if folded else "\n".join(block)
            fm[key] = text.strip()
            continue
        fm[key] = val.strip().strip('"').strip("'")
        i += 1
    return fm


def split_frontmatter(content: str):
    """Split markdown into frontmatter (dict) and body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        return parse_frontmatter_fields(match.group(1)), match.group(2)
    return {}, content

def derive_description(agent_name: str, body: str, fm: dict) -> str:
    if fm.get("description"):
        return fm["description"].strip().strip('"')

    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()

    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:160]

    return f"Agent {agent_name}"

def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_multiline(value: str) -> str:
    text = value.replace("\r\n", "\n").strip("\n")
    if '"""' in text:
        text = text.replace('"""', "'''")
    return '"""\n' + text + '\n"""'


def render_codex_agent(agent_name: str, body: str, description: str) -> str:
    profile = {**DEFAULT_CODEX_AGENT_PROFILE, **CODEX_AGENT_PROFILES.get(agent_name, {})}
    lines = [
        f"name = {toml_string(agent_name)}",
        f"description = {toml_string(description)}",
        f"model = {toml_string(str(profile.get('model', 'gpt-5.6')))}",
        f"model_reasoning_effort = {toml_string(str(profile.get('reasoning_effort', 'medium')))}",
        f"developer_instructions = {toml_multiline(body)}",
        "",
    ]
    return "\n".join(lines)

def normalize_bool(value: str) -> str:
    normalized = value.strip().strip('"').lower()
    if normalized in ("true", "yes", "1"):
        return "true"
    if normalized in ("false", "no", "0"):
        return "false"
    return value.strip().strip('"')

def format_profile_bool(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return normalize_bool(str(value))

def resolve_cursor_profile(agent_name: str) -> dict:
    return {**DEFAULT_CURSOR_AGENT_PROFILE, **CURSOR_AGENT_PROFILES.get(agent_name, {})}

def render_cursor_agent(agent_name: str, body: str, fm: dict, description: str) -> str:
    profile = resolve_cursor_profile(agent_name)
    cursor_fm = {
        "name": fm.get("name", agent_name).strip().strip('"'),
        "description": description,
        "model": fm.get("model", str(profile["model"])).strip().strip('"'),
        "readonly": normalize_bool(fm["readonly"]) if "readonly" in fm else format_profile_bool(profile["readonly"]),
        "is_background": normalize_bool(fm["is_background"]) if "is_background" in fm else format_profile_bool(profile["is_background"]),
    }
    fm_lines = ["---"]
    for key in CURSOR_FRONTMATTER_KEYS:
        fm_lines.append(f"{key}: {cursor_fm[key]}")
    fm_lines.append("---")
    source_footer = f"\n\n<!-- unicli-hub canonical source: hub/agents/{agent_name}.md -->\n"
    return "\n".join(fm_lines) + "\n\n" + body.rstrip() + source_footer

def resolve_grok_profile(agent_name: str) -> dict:
    return {**DEFAULT_GROK_AGENT_PROFILE, **GROK_AGENT_PROFILES.get(agent_name, {})}

def render_grok_agent(agent_name: str, body: str, fm: dict, description: str) -> str:
    profile = resolve_grok_profile(agent_name)
    grok_fm = {
        "name": fm.get("name", agent_name).strip().strip('"'),
        "description": description,
        "prompt_mode": fm.get("prompt_mode", str(profile.get("prompt_mode", "full"))).strip().strip('"'),
        "model": fm.get("model", str(profile.get("model", "inherit"))).strip().strip('"'),
        "permission_mode": fm.get("permission_mode", str(profile.get("permission_mode", "default"))).strip().strip('"'),
        "agents_md": normalize_bool(fm["agents_md"]) if "agents_md" in fm else format_profile_bool(profile.get("agents_md", True)),
    }
    fm_lines = ["---"]
    for key in GROK_FRONTMATTER_KEYS:
        fm_lines.append(f"{key}: {grok_fm[key]}")
    if "tools" in fm:
        fm_lines.append(f"tools: {fm['tools']}")
    fm_lines.append("---")
    source_footer = f"\n\n<!-- unicli-hub canonical source: hub/agents/{agent_name}.md -->\n"
    return "\n".join(fm_lines) + "\n\n" + body.rstrip() + source_footer

def render_all_agents():
    for src in sorted(AGENTS_SRC.glob("*.md")):
        a = src.stem
        PRODUCED_AGENTS.add(a)
        raw_content = src.read_text(encoding="utf-8")
        
        fm, body = split_frontmatter(raw_content)
        description = derive_description(a, body, fm)
        
        # Claude
        if TARGET_CLI in [None, "claude"]:
            fm_claude = fm.copy()
            fm_claude["name"] = a
            if "model" not in fm_claude:
                profile = {**DEFAULT_CLAUDE_AGENT_PROFILE, **CLAUDE_AGENT_PROFILES.get(a, {})}
                fm_claude["model"] = profile.get("model", "sonnet")
            
            if "tools" not in fm_claude:
                fm_claude["tools"] = "Read, Write, Edit, Bash, Glob, Grep"

            fm_lines = ["---"]
            for k, v in fm_claude.items(): fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["claude"] / f"{a}.md", "\n".join(fm_lines) + body)
        
        # Cursor
        if TARGET_CLI in [None, "cursor"]:
            compare_or_write(
                TARGETS["cursor"] / f"{a}.md",
                render_cursor_agent(a, body, fm, description),
            )
        
        # Codex
        if TARGET_CLI in [None, "codex"]:
            compare_or_write(TARGETS["codex"] / f"{a}.toml", render_codex_agent(a, body, description))

        # Grok
        if TARGET_CLI in [None, "grok"] and "grok" in TARGETS:
            compare_or_write(
                TARGETS["grok"] / f"{a}.md",
                render_grok_agent(a, body, fm, description),
            )

        # Kiro
        if TARGET_CLI in [None, "kiro"]:
            kiro_content = json.dumps({
                "name": a,
                "description": fm.get("description", description),
                "prompt": body.strip(),
                "tools": ["read", "write", "shell"],
                "includeMcpJson": True,
            }, indent=2)
            compare_or_write(TARGETS["kiro"] / f"{a}.json", kiro_content)

        # Antigravity
        if TARGET_CLI in [None, "antigravity"]:
            model_name = "gemini-3.1-pro"
            if a in ["researcher", "adr-impact-scanner", "tmf-knowledge-ingest"]:
                model_name = "gemini-3.5-flash"
                
            antigravity_content = json.dumps({
                "name": a,
                "description": fm.get("description", f"Agent {a}"),
                "system_prompt": body,
                "enable_mcp_tools": True,
                "enable_write_tools": True,
                "model": model_name
            }, indent=2)
            
            compare_or_write(TARGETS["antigravity"] / f"{a}.json", antigravity_content)

def reconcile():
    """Delete agents in target dirs that were not produced by this renderer."""
    global DRIFT
    targets_to_check = {k: v for k, v in TARGETS.items()
                        if TARGET_CLI is None or k == TARGET_CLI or (TARGET_CLI == "antigravity" and "antigravity" in k)}
    for cli, target_dir in targets_to_check.items():
        try:
            if not target_dir.exists():
                continue
        except Exception:
            continue
        for f in sorted(target_dir.iterdir()):
            if f.is_file() and f.suffix in [".md", ".json", ".toml"] and not f.name.startswith("skill-"):
                if f.stem not in PRODUCED_AGENTS:
                    if MODE == "fix":
                        f.unlink()
                        try:
                            print(f"removed stale agent: {f.relative_to(ROOT)}")
                        except ValueError:
                            print(f"removed stale agent: {f}")
                    else:
                        try:
                            print(f"DRIFT (stale agent): {f.relative_to(ROOT)}")
                        except ValueError:
                            print(f"DRIFT (stale agent): {f}")
                        DRIFT = True

def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: 
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = canonical_cli(arg.split("=", 1)[1])

    render_all_agents()
    reconcile()

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
