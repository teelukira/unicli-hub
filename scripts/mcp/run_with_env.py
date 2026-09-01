#!/usr/bin/env python3
"""Load worktree env files, then exec an MCP server command.

Precedence: parent process env > current worktree .env.local/.env >
primary worktree .env.local/.env.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys


def find_git_root(start: pathlib.Path) -> pathlib.Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def load_env_file(path: pathlib.Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def find_primary_worktree(repo_root: pathlib.Path) -> pathlib.Path | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    for line in completed.stdout.splitlines():
        if line.startswith("worktree "):
            return pathlib.Path(line.removeprefix("worktree ")).resolve()
    return None


def load_project_env(repo_root: pathlib.Path) -> dict[str, str]:
    repo_root = repo_root.resolve()
    inherited = dict(os.environ)
    file_env: dict[str, str] = {}
    primary = find_primary_worktree(repo_root)
    roots: list[pathlib.Path] = []
    if primary is not None and primary != repo_root:
        roots.append(primary)
    roots.append(repo_root)
    for root in roots:
        file_env.update(load_env_file(root / ".env"))
        file_env.update(load_env_file(root / ".env.local"))
    merged = {**file_env, **inherited}
    merged["UNICLI_HUB_ENV_LOADED"] = "1"
    return merged


def resolve_command(command: str, repo_root: pathlib.Path, env: dict[str, str]) -> str:
    normalized = command.replace("\\", "/")
    if "/" in normalized and not pathlib.Path(command).is_absolute():
        return str((repo_root / command.lstrip("./")).resolve())
    found = shutil.which(command, path=env.get("PATH"))
    return found or command


def main() -> None:
    if len(sys.argv) < 2:
        print("run_with_env: command is required", file=sys.stderr)
        raise SystemExit(2)

    repo_root = find_git_root(pathlib.Path.cwd())
    if repo_root is None:
        repo_root = pathlib.Path(__file__).resolve().parent.parent.parent

    env = load_project_env(repo_root)
    command = resolve_command(sys.argv[1], repo_root, env)
    args = [command, *sys.argv[2:]]
    completed = subprocess.run(args, env=env, cwd=str(repo_root))
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
