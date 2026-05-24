#!/usr/bin/env python3
"""
render_hooks.py - render hook configurations from hub/registry/hook-events.json.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REGISTRY = ROOT / "hub" / "registry" / "hook-events.json"

MODE = "fix"
TARGET_CLI = None
DRIFT = False


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def compare_or_write(target: pathlib.Path, content: str) -> None:
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {display_path(target)}")
            DRIFT = True
    else:
        target.write_text(content, encoding="utf-8")
        print(f"wrote: {display_path(target)}")


def load_registry() -> dict:
    if not REGISTRY.exists():
        print(f"ERROR: missing hook registry: {display_path(REGISTRY)}", file=sys.stderr)
        sys.exit(1)
    with REGISTRY.open(encoding="utf-8") as f:
        return json.load(f)


def render_claude_like(commands: dict, target: dict) -> str:
    hooks = {}
    for logical_event, target_event in target.get("events", {}).items():
        command = commands[logical_event]
        hooks[target_event] = [
            {
                "matcher": command.get("matcher", "*"),
                "hooks": [
                    {
                        "type": "command",
                        "command": command["command"],
                        "timeout": command.get("timeout", 10),
                    }
                ],
            }
        ]
    return json.dumps({"hooks": hooks}, indent=2, ensure_ascii=False) + "\n"


def render_cursor(commands: dict, target: dict) -> str:
    hooks = {}
    fail_closed = target.get("fail_closed", False)
    for logical_event, target_event in target.get("events", {}).items():
        command = commands[logical_event]
        entry = {
            "command": command["command"],
            "failClosed": fail_closed,
            "timeout": command.get("timeout", 10),
        }
        if "matcher" in command:
            entry["matcher"] = command["matcher"]
        hooks[target_event] = [entry]
    return json.dumps({"version": target.get("version", 1), "hooks": hooks}, indent=2, ensure_ascii=False) + "\n"


def render_target(commands: dict, name: str, target: dict) -> None:
    fmt = target.get("format")
    if fmt == "claude":
        content = render_claude_like(commands, target)
    elif fmt == "cursor":
        content = render_cursor(commands, target)
    else:
        print(f"ERROR: unsupported hook format for {name}: {fmt}", file=sys.stderr)
        sys.exit(1)
    compare_or_write(ROOT / target["path"], content)


def main() -> None:
    global MODE, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]:
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = arg.split("=", 1)[1]

    registry = load_registry()
    commands = registry.get("commands", {})
    for name, target in registry.get("targets", {}).items():
        if TARGET_CLI is not None and TARGET_CLI not in {name, "agy" if name == "antigravity" else name}:
            continue
        render_target(commands, name, target)

    if MODE == "check" and DRIFT:
        sys.exit(1)


if __name__ == "__main__":
    main()
