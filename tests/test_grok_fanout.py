#!/usr/bin/env python3
"""Grok Build fan-out: registry, renderer, and generated-file guard."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GrokFanoutTest(unittest.TestCase):
    def test_registries_declare_grok_targets(self):
        fanout = json.loads((REPO_ROOT / "hub" / "registry" / "fanout.json").read_text(encoding="utf-8"))
        self.assertEqual(fanout["agents"]["targets"]["grok"], ".grok/agents")
        self.assertEqual(fanout["skills"]["targets"]["grok"], ".grok/skills")
        self.assertEqual(
            fanout["mcp"]["targets"]["grok"],
            {"path": ".grok/config.toml", "format": "toml"},
        )

        hooks = json.loads((REPO_ROOT / "hub" / "registry" / "hook-events.json").read_text(encoding="utf-8"))
        grok = hooks["targets"]["grok"]
        self.assertEqual(grok["path"], ".grok/hooks/unicli-hub.json")
        self.assertEqual(grok["format"], "claude")
        self.assertEqual(grok["events"]["before_tool"], "PreToolUse")
        self.assertEqual(grok["events"]["stop"], "Stop")

        profiles = json.loads((REPO_ROOT / "hub" / "registry" / "agent-profiles.json").read_text(encoding="utf-8"))
        self.assertIn("grok", profiles["defaults"])
        self.assertEqual(profiles["defaults"]["grok"]["model"], "inherit")

    def test_render_grok_agent_frontmatter(self):
        render_agents = load_module(
            "render_agents",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_agents.py",
        )
        body = "# Reviewer\n\nReview the change set.\n"
        rendered = render_agents.render_grok_agent(
            "reviewer",
            body,
            {"description": "Review pull requests"},
            "Review pull requests",
        )
        self.assertIn("name: reviewer", rendered)
        self.assertIn("description: Review pull requests", rendered)
        self.assertIn("prompt_mode: full", rendered)
        self.assertIn("model: inherit", rendered)
        self.assertIn("permission_mode: default", rendered)
        self.assertIn("agents_md: true", rendered)
        self.assertIn("Review the change set.", rendered)
        self.assertIn("hub/agents/reviewer.md", rendered)

    def test_mcp_toml_target_is_shared_with_codex_shape(self):
        render_mcp = load_module(
            "render_mcp",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_mcp.py",
        )
        content = render_mcp.render_mcp_target(
            "grok",
            {"path": ".grok/config.toml", "format": "toml"},
            {
                "docs": {
                    "command": "uvx",
                    "args": ["example-server"],
                    "env": {"MODE": "test"},
                }
            },
        )
        self.assertIn("[mcp_servers.docs]", content)
        self.assertIn('command = "/bin/bash"', content)
        self.assertIn("unicli-hub-mcp", content)
        self.assertIn('MODE = "test"', content)

    def test_generated_file_guard_blocks_grok_paths(self):
        guard = load_module(
            "generated_file_guard",
            REPO_ROOT / "hub" / "hooks" / "generated_file_guard.py",
        )
        self.assertEqual(guard.normalize(r"C:\Users\teelu\orca\unicli-hub\.grok\config.toml"), ".grok/config.toml")
        self.assertEqual(guard.normalize("/tmp/unicli-hub/.grok/agents/reviewer.md"), ".grok/agents/reviewer.md")

        cases = [
            ".grok/config.toml",
            r"C:\work\unicli-hub\.grok\skills\html-report\SKILL.md",
            ".grok/hooks/unicli-hub.json",
            ".grok/rules/02-memory.md",
            ".grok/agents/reviewer.md",
        ]
        for path in cases:
            payload = json.dumps({"toolInput": {"file_path": path}})
            stdin = io.StringIO(payload)
            stdout = io.StringIO()
            stderr = io.StringIO()
            old_stdin = sys.stdin
            try:
                sys.stdin = stdin
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = guard.main()
            finally:
                sys.stdin = old_stdin
            self.assertEqual(code, 1, msg=path)
            self.assertIn("Generated file block", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
