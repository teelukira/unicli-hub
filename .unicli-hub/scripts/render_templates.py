#!/usr/bin/env python3
"""
render_templates.py — Assemble CLI entry points from templates and hub/ data.
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HUB = ROOT / "hub"
TEMPLATES = ROOT / ".unicli-hub" / "templates"

MODE = "fix"
TARGET_CLI = None
DRIFT = False

CURSOR_RULES = ROOT / ".cursor" / "rules"
KIRO_STEERING = ROOT / ".kiro" / "steering"

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

def assemble(tmpl_path: pathlib.Path, cli_name: str) -> str:
    if not tmpl_path.exists(): return ""
    tmpl = tmpl_path.read_text(encoding="utf-8")
    
    ctx = (HUB / "project-context.md").read_text(encoding="utf-8") if (HUB / "project-context.md").exists() else ""
    wf = (HUB / "core-workflow.md").read_text(encoding="utf-8") if (HUB / "core-workflow.md").exists() else ""
    
    memory = ""
    for mf in ["project-facts.md", "conventions.md", "jira-config.md", "glossary.md"]:
        p = HUB / "memory" / mf
        if p.exists(): memory += p.read_text(encoding="utf-8") + "\n\n"
        
    plugins = ""
    plugin_dir = HUB / "plugins" / cli_name
    if plugin_dir.is_dir():
        for pf in sorted(plugin_dir.glob("*.md")):
            plugins += pf.read_text(encoding="utf-8") + "\n\n"
            
    return (tmpl.replace("{{PROJECT_CONTEXT}}", ctx)
                .replace("{{CORE_WORKFLOW}}", wf)
                .replace("{{MEMORY}}", memory)
                .replace("{{PLUGINS}}", plugins))


def load_project_context() -> str:
    path = HUB / "project-context.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_memory() -> str:
    memory = ""
    for mf in ["project-facts.md", "conventions.md", "glossary.md"]:
        p = HUB / "memory" / mf
        if p.exists():
            memory += p.read_text(encoding="utf-8") + "\n\n"
    return memory


def cursor_rule(frontmatter: str, body: str) -> str:
    return frontmatter.rstrip() + "\n\n" + body.strip() + "\n"

def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: 
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = arg.split("=")[1]

    # mapping of: output_filename -> (template_path, cli_name)
    targets = {
        "CLAUDE.md": (TEMPLATES / "CLAUDE.md.tmpl", "claude"),
        "AGENTS.md": (TEMPLATES / "AGENTS.md.tmpl", "agents"),
    }

    target_aliases = {
        "antigravity": {"agents"},
        "agy": {"agents"},
        "codex": {"agents"},
        "claude": {"claude"},
    }

    for name, (tmpl, cli_name) in targets.items():
        if TARGET_CLI is not None and cli_name not in target_aliases.get(TARGET_CLI, {TARGET_CLI}):
            continue

        content = assemble(tmpl, cli_name)
        if content:
            compare_or_write(ROOT / name, content)

    if TARGET_CLI in [None, "cursor"]:
        ctx = load_project_context()
        if ctx:
            compare_or_write(
                CURSOR_RULES / "project-context.mdc",
                cursor_rule(
                    "---\nalwaysApply: true\ndescription: Project context generated from hub/project-context.md\n---",
                    ctx,
                ),
            )
        memory = load_memory()
        if memory:
            compare_or_write(
                CURSOR_RULES / "memory.mdc",
                cursor_rule(
                    "---\nalwaysApply: true\ndescription: Shared memory generated from hub/memory/*.md\n---",
                    memory,
                ),
            )

    if TARGET_CLI in [None, "kiro"]:
        ctx = load_project_context()
        if ctx:
            compare_or_write(KIRO_STEERING / "01-project-context.md", ctx.rstrip() + "\n")
        memory = load_memory()
        if memory:
            compare_or_write(KIRO_STEERING / "03-memory.md", memory.rstrip() + "\n")

    if TARGET_CLI in [None, "antigravity"]:
        import json
        plugin_manifest = json.dumps({
            "$schema": "https://antigravity.google/schemas/v1/plugin.json",
            "name": "unicli-hub",
            "description": "Generated plugin bundle"
        }, indent=2)
        compare_or_write(ROOT / ".agents" / "plugin.json", plugin_manifest)

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
