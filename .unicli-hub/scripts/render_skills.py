#!/usr/bin/env python3
"""
render_skills.py — Fan-out skills from hub/skills/ to all AI CLI targets.
Supports Claude, Gemini, Cursor, Antigravity (agy), Kiro, and Codex.
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL = ROOT / "hub" / "skills"

TARGETS = {
    "claude": ROOT / ".claude" / "skills",
    "gemini": ROOT / ".gemini" / "skills",
    "cursor": ROOT / ".cursor" / "skills",
    "agy": ROOT / ".agy" / "skills",
}

# Flat targets
KIRO_STEERING = ROOT / ".kiro" / "steering"
CODEX_PROMPTS = ROOT / ".codex" / "prompts"

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

def copy_references(src_dir: pathlib.Path, skill_name: str):
    ref_src = src_dir / "references"
    if not ref_src.is_dir():
        return

    for target_path in TARGETS.values():
        ref_dst_root = target_path / skill_name / "references"
        for ref_file in ref_src.rglob("*"):
            if not ref_file.is_file(): continue
            rel_path = ref_file.relative_to(ref_src)
            compare_or_write(ref_dst_root / rel_path, ref_file.read_text(encoding="utf-8"))

def main():
    global MODE, DRIFT
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: MODE = arg[2:]

    if not CANONICAL.is_dir():
        print(f"ERROR: {CANONICAL} not found", file=sys.stderr)
        sys.exit(1)

    # 1. Process flat markdown files
    for md_path in sorted(CANONICAL.glob("*.md")):
        skill_name = md_path.stem
        body = md_path.read_text(encoding="utf-8")
        for target_root in TARGETS.values():
            compare_or_write(target_root / skill_name / "SKILL.md", body + "\n")
        compare_or_write(KIRO_STEERING / f"skill-{skill_name}.md", body + "\n")
        compare_or_write(CODEX_PROMPTS / f"skill-{skill_name}.md", body + "\n")

    # 2. Process folder skills
    for skill_dir in sorted(CANONICAL.glob("*/")):
        if not skill_dir.is_dir() or skill_dir.name == "shared-references": continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file(): continue
        skill_name = skill_dir.name
        body = skill_md.read_text(encoding="utf-8")
        for target_root in TARGETS.values():
            compare_or_write(target_root / skill_name / "SKILL.md", body + "\n")
        compare_or_write(KIRO_STEERING / f"skill-{skill_name}.md", body + "\n")
        compare_or_write(CODEX_PROMPTS / f"skill-{skill_name}.md", body + "\n")
        copy_references(skill_dir, skill_name)

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
