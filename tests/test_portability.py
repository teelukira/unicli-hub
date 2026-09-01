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
                    "command": "python hub/hooks/pre_tool_use.py",
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
        self.assertEqual(payload["hooks"][0]["action"]["command"], "python hub/hooks/pre_tool_use.py")


if __name__ == "__main__":
    unittest.main()
