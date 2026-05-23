#!/usr/bin/env python3
"""
render_skills.py — Fan-out skills from hub/skills/ to all AI CLI targets.
Supports Claude, Gemini, Cursor, Antigravity, Kiro, and Codex.
"""

import sys
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CANONICAL = ROOT / "hub" / "skills"

TARGETS = {
    "claude": ROOT / ".claude" / "skills",
    "cursor": ROOT / ".cursor" / "skills",
    "antigravity": ROOT / ".agents" / "skills",
}

# Flat targets
KIRO_STEERING = ROOT / ".kiro" / "steering"
CODEX_PROMPTS = ROOT / ".codex" / "prompts"

MODE = "fix"
TARGET_CLI = None
DRIFT = False
PRODUCED_SKILLS: set = set()

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


def compare_or_write_bytes(target: pathlib.Path, content: bytes):
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_bytes() != content:
            try:
                print(f"DRIFT: {target.relative_to(ROOT)}")
            except ValueError:
                print(f"DRIFT: {target}")
            DRIFT = True
    else:
        target.write_bytes(content)
        try:
            print(f"wrote: {target.relative_to(ROOT)}")
        except ValueError:
            print(f"wrote: {target}")

def get_dependencies(content: str) -> list:
    # Look for depends_on: [skill1, skill2] or depends_on: skill1
    match = re.search(r"depends_on:\s*\[?(.*?)\]?\s*$", content, re.MULTILINE)
    if match:
        deps = [d.strip() for d in match.group(1).split(",") if d.strip()]
        return deps
    return []

def collect_dependency_refs(skill_name: str, visited=None) -> list:
    if visited is None: visited = set()
    if skill_name in visited: return []
    visited.add(skill_name)
    
    ref_paths = []
    
    # Try folder skill
    skill_dir = CANONICAL / skill_name
    content = ""
    if skill_dir.is_dir():
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
        ref_path = skill_dir / "references"
        if ref_path.is_dir():
            ref_paths.append(ref_path)
    else:
        # Try flat file skill
        skill_md = CANONICAL / f"{skill_name}.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")

    deps = get_dependencies(content)
    for dep in deps:
        ref_paths.extend(collect_dependency_refs(dep, visited))
    
    return ref_paths

def copy_references(skill_name: str, current_skill_content: str):
    # Collect all reference folders from dependencies
    deps = get_dependencies(current_skill_content)
    all_ref_srcs = []
    visited = {skill_name} # Don't re-process current skill in dependency search
    for dep in deps:
        all_ref_srcs.extend(collect_dependency_refs(dep, visited))
    
    # Add current skill's own references if it's a folder skill
    own_ref_src = CANONICAL / skill_name / "references"
    if own_ref_src.is_dir():
        all_ref_srcs.insert(0, own_ref_src) # Current skill refs take precedence or at least are added

    if not all_ref_srcs:
        return

    targets_to_process = []
    if TARGET_CLI is None:
        targets_to_process = list(TARGETS.values())
    elif TARGET_CLI in TARGETS:
        targets_to_process = [TARGETS[TARGET_CLI]]

    for target_path in targets_to_process:
        ref_dst_root = target_path / skill_name / "references"
        for ref_src in all_ref_srcs:
            for ref_file in ref_src.rglob("*"):
                if not ref_file.is_file(): continue
                rel_path = ref_file.relative_to(ref_src)
                compare_or_write(ref_dst_root / rel_path, ref_file.read_text(encoding="utf-8"))


def copy_folder_skill_contents(skill_name: str):
    skill_dir = CANONICAL / skill_name
    if not skill_dir.is_dir():
        return

    targets_to_process = []
    if TARGET_CLI is None:
        targets_to_process = list(TARGETS.values())
    elif TARGET_CLI in TARGETS:
        targets_to_process = [TARGETS[TARGET_CLI]]

    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(skill_dir)
        if rel_path.parts[0] in ["SKILL.md", "references"]:
            continue
        if "__pycache__" in path.parts or path.name.endswith(".pyc"):
            continue
        if path.name == ".DS_Store":
            continue

        data = path.read_bytes()
        for target_root in targets_to_process:
            dst_path = target_root / skill_name / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            compare_or_write_bytes(dst_path, data)


def reconcile():
    """Delete skills in target dirs that were not produced by this renderer."""
    global DRIFT
    targets_to_check = {}
    if TARGET_CLI is None:
        targets_to_check = dict(TARGETS)
    elif TARGET_CLI in TARGETS:
        targets_to_check = {TARGET_CLI: TARGETS[TARGET_CLI]}

    for _cli, target_dir in targets_to_check.items():
        if not target_dir.exists():
            continue
        for item in sorted(target_dir.iterdir()):
            if item.is_dir() and item.name not in PRODUCED_SKILLS:
                if MODE == "fix":
                    shutil.rmtree(item)
                    try:
                        print(f"removed stale skill: {item.relative_to(ROOT)}")
                    except ValueError:
                        print(f"removed stale skill: {item}")
                else:
                    try:
                        print(f"DRIFT (stale skill): {item.relative_to(ROOT)}")
                    except ValueError:
                        print(f"DRIFT (stale skill): {item}")
                    DRIFT = True

    if TARGET_CLI in [None, "kiro"] and KIRO_STEERING.exists():
        for f in sorted(KIRO_STEERING.glob("skill-*.md")):
            skill_name = f.stem[len("skill-"):]
            if skill_name not in PRODUCED_SKILLS:
                if MODE == "fix":
                    f.unlink()
                    try:
                        print(f"removed stale skill: {f.relative_to(ROOT)}")
                    except ValueError:
                        print(f"removed stale skill: {f}")
                else:
                    try:
                        print(f"DRIFT (stale skill): {f.relative_to(ROOT)}")
                    except ValueError:
                        print(f"DRIFT (stale skill): {f}")
                    DRIFT = True

    if TARGET_CLI in [None, "codex"] and CODEX_PROMPTS.exists():
        for f in sorted(CODEX_PROMPTS.glob("skill-*.md")):
            skill_name = f.stem[len("skill-"):]
            if skill_name not in PRODUCED_SKILLS:
                if MODE == "fix":
                    f.unlink()
                    try:
                        print(f"removed stale skill: {f.relative_to(ROOT)}")
                    except ValueError:
                        print(f"removed stale skill: {f}")
                else:
                    try:
                        print(f"DRIFT (stale skill): {f.relative_to(ROOT)}")
                    except ValueError:
                        print(f"DRIFT (stale skill): {f}")
                    DRIFT = True


def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]: 
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = arg.split("=")[1]

    if not CANONICAL.is_dir():
        print(f"ERROR: {CANONICAL} not found", file=sys.stderr)
        sys.exit(1)

    # Determine which targets to process
    target_roots = []
    if TARGET_CLI is None:
        target_roots = list(TARGETS.values())
    elif TARGET_CLI in TARGETS:
        target_roots = [TARGETS[TARGET_CLI]]

    # 1. Process flat markdown files
    for md_path in sorted(CANONICAL.glob("*.md")):
        skill_name = md_path.stem
        PRODUCED_SKILLS.add(skill_name)
        body = md_path.read_text(encoding="utf-8")
        for target_root in target_roots:
            compare_or_write(target_root / skill_name / "SKILL.md", body + "\n")

        if TARGET_CLI in [None, "kiro"]:
            compare_or_write(KIRO_STEERING / f"skill-{skill_name}.md", body + "\n")
        if TARGET_CLI in [None, "codex"]:
            compare_or_write(CODEX_PROMPTS / f"skill-{skill_name}.md", body + "\n")

        copy_references(skill_name, body)

    # 2. Process folder skills
    for skill_dir in sorted(CANONICAL.glob("*/")):
        if not skill_dir.is_dir() or skill_dir.name == "shared-references": continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file(): continue
        skill_name = skill_dir.name
        PRODUCED_SKILLS.add(skill_name)
        body = skill_md.read_text(encoding="utf-8")
        for target_root in target_roots:
            compare_or_write(target_root / skill_name / "SKILL.md", body + "\n")

        if TARGET_CLI in [None, "kiro"]:
            compare_or_write(KIRO_STEERING / f"skill-{skill_name}.md", body + "\n")
        if TARGET_CLI in [None, "codex"]:
            compare_or_write(CODEX_PROMPTS / f"skill-{skill_name}.md", body + "\n")

        copy_references(skill_name, body)
        copy_folder_skill_contents(skill_name)

    reconcile()

    if MODE == "check" and DRIFT:
        sys.exit(1)

if __name__ == "__main__":
    main()
