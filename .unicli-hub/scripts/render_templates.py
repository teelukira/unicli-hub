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
DRIFT = False

def compare_or_write(target: pathlib.Path, content: str):
    global DRIFT
    if MODE == "check":
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {target.relative_to(ROOT)}")
            DRIFT = True
    else:
        target.write_text(content, encoding="utf-8")
        print(f"wrote: {target.relative_to(ROOT)}")

def assemble(tmpl_path: pathlib.Path) -> str:
    if not tmpl_path.exists(): return ""
    tmpl = tmpl_path.read_text(encoding="utf-8")
    
    ctx = (HUB / "project-context.md").read_text(encoding="utf-8") if (HUB / "project-context.md").exists() else ""
    wf = (HUB / "core-workflow.md").read_text(encoding="utf-8") if (HUB / "core-workflow.md").exists() else ""
    
    memory = ""
    for mf in ["project-facts.md", "conventions.md", "jira-config.md", "glossary.md"]:
        p = HUB / "memory" / mf
        if p.exists(): memory += p.read_text(encoding="utf-8") + "\n\n"
        
    return tmpl.replace("{{PROJECT_CONTEXT}}", ctx).replace("{{CORE_WORKFLOW}}", wf).replace("{{MEMORY}}", memory)

def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: MODE = arg[2:]

    targets = {
        "CLAUDE.md": TEMPLATES / "CLAUDE.md.tmpl",
        "GEMINI.md": TEMPLATES / "GEMINI.md.tmpl",
        "AGY.md": TEMPLATES / "AGY.md.tmpl",
        "AGENTS.md": TEMPLATES / "AGENTS.md.tmpl",
    }

    for name, tmpl in targets.items():
        content = assemble(tmpl)
        if content: compare_or_write(ROOT / name, content)

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
