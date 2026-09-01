#!/usr/bin/env python3
"""Latest CLI spec mappings for Codex, Kiro, Antigravity, and Claude."""

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


class CliSpecTest(unittest.TestCase):
    def test_fanout_uses_current_native_paths(self):
        fanout = json.loads((REPO_ROOT / "hub" / "registry" / "fanout.json").read_text(encoding="utf-8"))
        self.assertEqual(fanout["skills"]["targets"]["codex"], ".agents/skills")
        self.assertEqual(fanout["skills"]["targets"]["kiro"], ".kiro/skills")
        self.assertEqual(fanout["skills"]["targets"]["antigravity"], ".agents/skills")
        self.assertEqual(fanout["agents"]["targets"]["codex"], ".codex/agents")
        self.assertEqual(
            fanout["mcp"]["targets"]["antigravity"],
            {"path": ".agents/mcp_config.json", "format": "antigravity_json"},
        )

    def test_codex_agent_is_toml(self):
        render_agents = load_module(
            "render_agents",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_agents.py",
        )
        rendered = render_agents.render_codex_agent(
            "reviewer",
            "Review the change set.\n",
            "Review pull requests",
        )
        self.assertIn('name = "reviewer"', rendered)
        self.assertIn("developer_instructions = ", rendered)
        self.assertIn("model_reasoning_effort = ", rendered)
        self.assertNotIn("codex_role:", rendered)
        self.assertTrue(rendered.strip().startswith("name = "))

    def test_kiro_agent_uses_prompt_and_shell_tag(self):
        render_agents = load_module(
            "render_agents",
            REPO_ROOT / ".unicli-hub" / "scripts" / "render_agents.py",
        )
        payload = json.loads(
            json.dumps(
                {
                    "name": "reviewer",
                    "description": "Review pull requests",
                    "prompt": "Review the change set.",
                    "tools": ["read", "write", "shell"],
                    "includeMcpJson": True,
                }
            )
        )
        self.assertEqual(payload["tools"], ["read", "write", "shell"])
        self.assertIn("prompt", payload)
        self.assertNotIn("system_prompt", payload)
        self.assertTrue(hasattr(render_agents, "render_codex_agent"))


if __name__ == "__main__":
    unittest.main()
