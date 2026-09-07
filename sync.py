#!/usr/bin/env python3
"""UniCLI-Hub sync orchestrator. Works on Windows and POSIX."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SCRIPTS = ROOT / ".unicli-hub" / "scripts"
RENDERERS = (
    "render_agents.py",
    "render_skills.py",
    "render_static.py",
    "render_hooks.py",
    "render_mcp.py",
    "render_templates.py",
)
LEGACY_DIRS = (
    ".agents/plugins",
    ".antigravitycli",
    ".agy",
    ".gemini",
    ".cursor/hooks",
)
LEGACY_FILES = (
    "GEMINI.md",
    "AGY.md",
)
PYCACHE_ROOTS = (
    "hub",
    ".cursor",
    ".agents",
    ".claude",
    ".grok",
    ".kiro",
    ".codex",
)


def parse_args(argv: list[str]) -> tuple[str, str | None]:
    mode = "fix"
    target = None
    for arg in argv:
        if arg == "--check":
            mode = "check"
        elif arg == "--fix":
            mode = "fix"
        elif arg.startswith("--target="):
            target = arg.split("=", 1)[1]
    return mode, target


def cleanup_legacy() -> None:
    for rel in LEGACY_DIRS:
        path = ROOT / rel
        if path.is_dir():
            print(f"Cleaning legacy directory: {rel}")
            shutil.rmtree(path, ignore_errors=True)
    for rel in LEGACY_FILES:
        path = ROOT / rel
        if path.is_file():
            print(f"Removing legacy file: {rel}")
            path.unlink()


def cleanup_pycache() -> None:
    for rel in PYCACHE_ROOTS:
        root = ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("__pycache__"):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


def run_renderer(script: str, mode: str, target: str | None) -> None:
    cmd = [sys.executable, str(SCRIPTS / script), f"--{mode}"]
    if target:
        cmd.append(f"--target={target}")
    completed = subprocess.run(cmd, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    mode, target = parse_args(sys.argv[1:])
    suffix = f", --target={target}" if target else ""
    print(f"--- UniCLI-Hub Sync ({mode}{suffix}) ---")

    if mode == "fix" and target is None:
        cleanup_legacy()
        cleanup_pycache()

    for script in RENDERERS:
        run_renderer(script, mode, target)

    print("--- Sync Complete ---")


if __name__ == "__main__":
    main()
