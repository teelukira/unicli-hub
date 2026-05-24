#!/usr/bin/env python3
"""
render_agents.py — Fan-out agents from hub/agents/ to all AI CLI targets.
"""

import sys
import pathlib
import json
import re
import shutil

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
        "antigravity": ".agents/agents",
        "antigravity_global": "~/.gemini/antigravity-cli/agents",
    }).items()
}

MODELS = {
    "claude": {
        "researcher": "claude-3-5-sonnet-20241022",
        "codegen": "claude-3-5-sonnet-20241022",
        "reviewer": "claude-3-5-sonnet-20241022"
    },
}

AGENT_PROFILES = read_json(AGENT_PROFILES_REGISTRY)
CODEX_AGENT_PROFILES = AGENT_PROFILES.get("codex", {})
DEFAULT_CODEX_AGENT_PROFILE = AGENT_PROFILES.get("defaults", {}).get("codex", {
    "model": "gpt-5.4-mini",
    "reasoning_effort": "medium",
    "role": "general",
})

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

def render_codex_agent(agent_name: str, body: str, description: str) -> str:
    profile = CODEX_AGENT_PROFILES.get(agent_name, DEFAULT_CODEX_AGENT_PROFILE)
    fm = {
        "name": agent_name,
        "description": description,
        "codex_model": profile["model"],
        "codex_reasoning_effort": profile["reasoning_effort"],
        "codex_role": profile["role"],
    }
    fm_lines = ["---"]
    for key, value in fm.items():
        fm_lines.append(f"{key}: {value}")
    fm_lines.append("---")
    guidance = (
        "\n## Codex Subagent Execution Profile\n\n"
        f"- Spawn with `model=\"{profile['model']}\"` and "
        f"`reasoning_effort=\"{profile['reasoning_effort']}\"` when this prompt is delegated via "
        "`multi_agent_v1.spawn_agent`.\n"
        "- Keep task scope narrow and load only the referenced project files before editing or reviewing.\n\n"
    )
    return "\n".join(fm_lines) + "\n" + guidance + body

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
            if a not in MODELS["claude"]:
                 fm_claude["model"] = "claude-3-5-sonnet-20241022"
            else:
                 fm_claude["model"] = MODELS["claude"][a]
            
            fm_lines = ["---"]
            for k, v in fm_claude.items(): fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["claude"] / f"{a}.md", "\n".join(fm_lines) + body)
        
        # Cursor
        if TARGET_CLI in [None, "cursor"]:
            fm_cursor = fm.copy()
            fm_cursor["description"] = fm.get("description", f"Agent {a}")
            fm_cursor["source"] = f"hub/agents/{a}.md"
            
            fm_lines = ["---"]
            for k, v in fm_cursor.items(): fm_lines.append(f"{k}: {v}")
            fm_lines.append("---\n")
            compare_or_write(TARGETS["cursor"] / f"{a}.md", "\n".join(fm_lines) + body)
        
        # Codex
        if TARGET_CLI in [None, "codex"]:
            compare_or_write(TARGETS["codex"] / f"{a}.md", render_codex_agent(a, body, description))

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
            
            # Write to agents/
            compare_or_write(TARGETS["antigravity"] / a / "agent.json", antigravity_content)
            try:
                compare_or_write(TARGETS["antigravity_global"] / a / "agent.json", antigravity_content)
            except Exception:
                pass # Ignore global write errors
                

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
        if cli in ("antigravity", "antigravity_global"):
            for subdir in sorted(target_dir.iterdir()):
                if subdir.is_dir() and subdir.name not in PRODUCED_AGENTS:
                    if MODE == "fix":
                        shutil.rmtree(subdir)
                        try:
                            print(f"removed stale agent: {subdir.relative_to(ROOT)}")
                        except ValueError:
                            print(f"removed stale agent: {subdir}")
                    else:
                        try:
                            print(f"DRIFT (stale agent): {subdir.relative_to(ROOT)}")
                        except ValueError:
                            print(f"DRIFT (stale agent): {subdir}")
                        DRIFT = True
        else:
            for f in sorted(target_dir.iterdir()):
                if f.is_file() and f.suffix == ".md" and not f.name.startswith("skill-"):
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
            TARGET_CLI = arg.split("=")[1]

    render_all_agents()
    reconcile()

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
