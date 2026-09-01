#!/usr/bin/env python3
"""
render_mcp.py — Fan-out MCP configurations from hub/mcp-servers.json to all targets.
"""

import copy
import json
import os
import pathlib
import re
import subprocess
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from cli_names import canonical_cli

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FANOUT_REGISTRY = ROOT / "hub" / "registry" / "fanout.json"
PROJECT_ENV_LAUNCHER = "scripts/mcp/run_with_env.py"

DEFAULT_MCP_FANOUT = {
    "source": "hub/mcp-servers.json",
    "targets": {
        "claude": {"path": ".mcp.json", "format": "json"},
        "cursor": {"path": ".cursor/mcp.json", "format": "json"},
        "antigravity": {"path": ".agents/mcp_config.json", "format": "antigravity_json"},
        "kiro": {"path": ".kiro/settings/mcp.json", "format": "json"},
        "codex": {"path": ".codex/config.toml", "format": "toml"},
        "grok": {"path": ".grok/config.toml", "format": "toml"},
    },
}

MODE = "fix"
TARGET_CLI = None
DRIFT = False


def resolve_path(path_value: str) -> pathlib.Path:
    path = pathlib.Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def read_json(path: pathlib.Path) -> dict:
    if path.exists():
        with path.open(encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def load_mcp_fanout() -> dict:
    registry = read_json(FANOUT_REGISTRY).get("mcp", {})
    return {
        "source": registry.get("source", DEFAULT_MCP_FANOUT["source"]),
        "targets": registry.get("targets", DEFAULT_MCP_FANOUT["targets"]),
    }


def load_env(path: pathlib.Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env


def find_primary_worktree(repo_root: pathlib.Path):
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


def load_project_env(repo_root: pathlib.Path) -> dict:
    repo_root = repo_root.resolve()
    primary_root = find_primary_worktree(repo_root)
    roots = []
    if primary_root is not None and primary_root != repo_root:
        roots.append(primary_root)
    roots.append(repo_root)

    env = {}
    for root in roots:
        env.update(load_env(root / ".env"))
        env.update(load_env(root / ".env.local"))
    return env


def substitute_env(data, env_vars: dict):
    if isinstance(data, dict):
        return {k: substitute_env(v, env_vars) for k, v in data.items()}
    if isinstance(data, list):
        return [substitute_env(i, env_vars) for i in data]
    if isinstance(data, str):
        def replacer(match):
            var_name = match.group(1)
            val = os.environ.get(var_name) or env_vars.get(var_name)
            if val is None:
                print(
                    f"ERROR: Missing environment variable '${var_name}' "
                    "in .env.local or shell environment."
                )
                sys.exit(1)
            return val
        return re.sub(r"\${(\w+)}", replacer, data)
    return data


def _display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def compare_or_write(target: pathlib.Path, content: str):
    global DRIFT
    target.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "check":
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {_display_path(target)}")
            DRIFT = True
    else:
        target.write_text(content, encoding="utf-8")
        print(f"wrote: {_display_path(target)}")


def strip_meta(data):
    """Recursively strip unicli-hub meta keys (_comment, _overrides, _targets, etc.)."""
    if isinstance(data, dict):
        return {k: strip_meta(v) for k, v in data.items() if not k.startswith("_")}
    if isinstance(data, list):
        return [strip_meta(i) for i in data]
    return data


strip_comments = strip_meta


def apply_overrides(server: dict, cli: str) -> dict:
    overrides = server.get("_overrides", {})
    if cli not in overrides:
        return server
    merged = copy.deepcopy(server)
    merged.update(overrides[cli])
    return merged


def wrap_project_env(server: dict) -> dict:
    if (
        server.get("_project_env", True) is False
        or server.get("type") == "http"
        or "command" not in server
    ):
        return server

    wrapped = copy.deepcopy(server)
    command = wrapped["command"]
    args = wrapped.get("args", [])
    wrapped["command"] = "python"
    wrapped["args"] = [
        PROJECT_ENV_LAUNCHER,
        command,
        *args,
    ]
    return wrapped


def filter_servers(raw_servers: dict, cli: str) -> dict:
    result = {}
    for name, cfg in raw_servers.items():
        targets = cfg.get("_targets")
        if targets is not None:
            allowed = {canonical_cli(item) or item for item in targets}
            if cli not in allowed:
                continue
        result[name] = wrap_project_env(apply_overrides(cfg, cli))
    return result


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: list) -> str:
    return "[" + ", ".join(toml_string(str(v)) for v in values) + "]"


def render_codex_toml(servers: dict) -> str:
    lines = [
        "# MCP servers - generated by render_mcp.py, do not edit directly",
        "",
    ]

    for name, cfg in servers.items():
        clean = strip_meta(cfg)
        lines.append(f"[mcp_servers.{name}]")

        if clean.get("type") == "http":
            url = clean.get("url") or clean.get("httpUrl") or clean.get("serverUrl")
            if url:
                lines.append(f"url = {toml_string(str(url))}")
            token_env = clean.get("bearer_token_env_var") or clean.get("bearerTokenEnvVar")
            if token_env:
                lines.append(f"bearer_token_env_var = {toml_string(str(token_env))}")
        else:
            if "command" in clean:
                lines.append(f"command = {toml_string(str(clean['command']))}")
            if "args" in clean:
                lines.append(f"args = {toml_array(clean['args'])}")

        if "enabled" in clean:
            lines.append(f"enabled = {'true' if clean['enabled'] else 'false'}")
        if "startup_timeout_sec" in clean:
            lines.append(f"startup_timeout_sec = {int(clean['startup_timeout_sec'])}")
        if "tool_timeout_sec" in clean:
            lines.append(f"tool_timeout_sec = {int(clean['tool_timeout_sec'])}")

        env = clean.get("env") or {}
        if env:
            lines.append(f"[mcp_servers.{name}.env]")
            for key, value in env.items():
                lines.append(f"{key} = {toml_string(str(value))}")

        headers = clean.get("headers") or {}
        if headers:
            lines.append(f"[mcp_servers.{name}.headers]")
            for key, value in headers.items():
                lines.append(f"{key} = {toml_string(str(value))}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_antigravity_json(servers: dict) -> str:
    ag_servers = {}
    for name, cfg in servers.items():
        ag_cfg = dict(cfg)
        server_type = ag_cfg.pop("type", None)
        if server_type == "http":
            ag_cfg["serverUrl"] = ag_cfg.pop("url", ag_cfg.pop("httpUrl", ""))
        ag_servers[name] = ag_cfg
    clean = strip_meta(ag_servers)
    return json.dumps({"mcpServers": clean}, indent=2, ensure_ascii=False) + "\n"


def render_mcp_json(servers: dict) -> str:
    clean = strip_meta(servers)
    return json.dumps({"mcpServers": clean}, indent=2, ensure_ascii=False) + "\n"


def render_mcp_target(cli: str, target_cfg: dict, raw_servers_subst: dict) -> str:
    fmt = target_cfg.get("format", "json")
    cli_servers = filter_servers(raw_servers_subst, cli)
    if fmt == "json":
        return render_mcp_json(cli_servers)
    if fmt == "antigravity_json":
        return render_antigravity_json(cli_servers)
    if fmt == "toml":
        return render_codex_toml(cli_servers)
    print(f"ERROR: unsupported MCP target format '{fmt}' for cli '{cli}'", file=sys.stderr)
    sys.exit(1)


def main():
    global MODE, DRIFT, TARGET_CLI
    for arg in sys.argv[1:]:
        if arg in ["--fix", "--check"]:
            MODE = arg[2:]
        elif arg.startswith("--target="):
            TARGET_CLI = canonical_cli(arg.split("=", 1)[1])

    mcp_fanout = load_mcp_fanout()
    canonical = resolve_path(mcp_fanout["source"])
    if not canonical.exists():
        print(f"ERROR: {canonical} not found")
        sys.exit(1)

    env_vars = load_project_env(ROOT)
    src = read_json(canonical)
    raw_servers = src.get("mcpServers", {})
    raw_servers_subst = substitute_env(raw_servers, env_vars)

    for cli, target_cfg in sorted(mcp_fanout["targets"].items()):
        if TARGET_CLI not in [None, cli]:
            continue
        target_path = resolve_path(target_cfg["path"])
        content = render_mcp_target(cli, target_cfg, raw_servers_subst)
        compare_or_write(target_path, content)

    if MODE == "check" and DRIFT:
        sys.exit(1)


if __name__ == "__main__":
    main()
