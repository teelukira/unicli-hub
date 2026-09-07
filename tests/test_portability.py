#!/usr/bin/env python3
"""Windows-safe sync, hook, and renderer helpers."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortabilityTest(unittest.TestCase):
    def test_auto_update_imports_without_fcntl(self):
        module = load_module("auto_update", REPO_ROOT / "hub" / "hooks" / "auto_update.py")
        self.assertTrue(hasattr(module, "FileLock"))
        self.assertFalse(hasattr(module, "fcntl"))

    def test_canonical_cli_aliases_agy(self):
        module = load_module(
            "cli_names",
            REPO_ROOT / ".unicli-hub" / "scripts" / "cli_names.py",
        )
        self.assertEqual(module.canonical_cli("agy"), "antigravity")
        self.assertEqual(module.canonical_cli("grok"), "grok")

    def test_folded_frontmatter_description(self):
        render_agents = load_module(
            "render_agents",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_agents.py",
        )
        content = (
            "---\n"
            "name: reviewer\n"
            "description: >-\n"
            "  Review pull requests\n"
            "  and report findings.\n"
            "---\n"
            "Body here.\n"
        )
        fm, body = render_agents.split_frontmatter(content)
        self.assertEqual(fm["name"], "reviewer")
        self.assertIn("Review pull requests", fm["description"])
        self.assertIn("report findings", fm["description"])
        self.assertTrue(body.startswith("Body here."))

    def test_kiro_hook_format(self):
        render_hooks = load_module(
            "render_hooks",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_hooks.py",
        )
        content = render_hooks.render_kiro(
            {
                "before_tool": {
                    "script": "hub/hooks/pre_tool_use.py",
                    "timeout": 20,
                    "matcher": "*",
                }
            },
            {"events": {"before_tool": "PreToolUse"}},
        )
        payload = json.loads(content)
        self.assertEqual(payload["version"], "v1")
        self.assertEqual(payload["hooks"][0]["trigger"], "PreToolUse")
        self.assertNotIn("matcher", payload["hooks"][0])
        self.assertIn("pre_tool_use.py", payload["hooks"][0]["action"]["command"])

    def test_hook_commands_are_absolute_and_shell_free(self):
        render_hooks = load_module(
            "render_hooks",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_hooks.py",
        )
        registry = json.loads(
            (REPO_ROOT / "hub" / "registry" / "hook-events.json").read_text(encoding="utf-8")
        )
        for name, entry in registry["commands"].items():
            self.assertNotIn("command", entry, name)
            script = REPO_ROOT / entry["script"]
            self.assertTrue(script.is_file(), f"{name}: missing {script}")

            command = render_hooks.hook_command(entry)
            interpreter, _, target = command.partition('" "')
            interpreter = interpreter.lstrip('"')
            target = target.rstrip('"')

            # A bare `python`/`python3` name resolves differently per OS, and a
            # relative script path breaks when the CLI runs the hook from a
            # subdirectory. Both must be absolute.
            self.assertTrue(Path(interpreter).is_absolute(), f"{name}: {interpreter}")
            self.assertTrue(Path(interpreter).exists(), f"{name}: {interpreter}")
            self.assertEqual(Path(target), script.resolve())
            # No shell builtins, no bash, no git on PATH at hook time.
            for token in ("bash -c", "command -v", "git rev-parse"):
                self.assertNotIn(token, command, name)

    def test_claude_render_passes_the_registry_command_through(self):
        render_hooks = load_module(
            "render_hooks",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_hooks.py",
        )
        registry = json.loads(
            (REPO_ROOT / "hub" / "registry" / "hook-events.json").read_text(encoding="utf-8")
        )
        commands = registry["commands"]
        target = registry["targets"]["claude"]
        payload = json.loads(render_hooks.render_claude_like(commands, target))
        group = payload["hooks"]["PreToolUse"][0]
        self.assertNotIn("matcher", group)
        self.assertEqual(
            group["hooks"][0]["command"], render_hooks.hook_command(commands["before_tool"])
        )


if __name__ == "__main__":
    unittest.main()
