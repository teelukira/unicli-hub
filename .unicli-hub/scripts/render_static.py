#!/usr/bin/env python3
"""
render_static.py - render static directory copies declared in fanout.json.
"""

import json
import pathlib
import shutil
import sys
from fnmatch import fnmatch

_SCRIPTS = pathlib.Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from cli_names import canonical_cli

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FANOUT_REGISTRY = ROOT / "hub" / "registry" / "fanout.json"

MODE = "fix"
TARGET_CLI = None
DRIFT = False


def resolve_path(path_value: str) -> pathlib.Path:
    path = pathlib.Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def compare_or_write(target: pathlib.Path, content: bytes) -> None:
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_bytes() != content:
            print(f"DRIFT: {display_path(target)}")
            DRIFT = True
    else:
        target.write_bytes(content)
        print(f"wrote: {display_path(target)}")


def remove_or_report(path: pathlib.Path, label: str) -> None:
    global DRIFT
    if MODE == "check":
        print(f"DRIFT (stale {label}): {display_path(path)}")
        DRIFT = True
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    print(f"removed stale {label}: {display_path(path)}")


def load_registry() -> dict:
    if not FANOUT_REGISTRY.exists():
        return {}
    with FANOUT_REGISTRY.open(encoding="utf-8") as f:
        return json.load(f)


def render_static_copy(name: str, config: dict) -> None:
    source = resolve_path(config["source"])
    target = resolve_path(config["target"])
    ignore_stale_globs = config.get("ignore_stale_globs", [])
    if not source.is_dir():
        print(f"ERROR: missing static source for {name}: {display_path(source)}", file=sys.stderr)
        sys.exit(1)

    produced = set()
    for src in sorted(source.rglob("*")):
        if not src.is_file():
            continue
        if "__pycache__" in src.parts or src.name.endswith(".pyc") or src.name == ".DS_Store":
            continue
        rel = src.relative_to(source)
        produced.add(rel.as_posix())
        compare_or_write(target / rel, src.read_bytes())

    if not target.exists():
        return
    for dst in sorted(target.rglob("*"), reverse=True):
        if dst == target:
            continue
        rel = dst.relative_to(target).as_posix()
        if any(fnmatch(rel, pattern) for pattern in ignore_stale_globs):
            continue
        if dst.is_file() and rel not in produced:
            remove_or_report(dst, name)
        elif dst.is_dir() and not any(dst.iterdir()):
            remove_or_report(dst, name)


def main() -> None:
    global MODE, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]:
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = canonical_cli(arg.split("=", 1)[1])

    registry = load_registry()
    for name, config in registry.get("static_copies", {}).items():
        owner = name.split("_", 1)[0]
        if TARGET_CLI is not None and TARGET_CLI not in {name, owner}:
            continue
        render_static_copy(name, config)

    if MODE == "check" and DRIFT:
        sys.exit(1)


if __name__ == "__main__":
    main()
