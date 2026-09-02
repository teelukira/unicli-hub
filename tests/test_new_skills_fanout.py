#!/usr/bin/env python3
"""New generic skills exist canonically and fan out."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("confluence-page", "email-html-report", "html-report")


class NewSkillsFanoutTest(unittest.TestCase):
    def test_canonical_skill_md(self):
        for name in SKILLS:
            path = REPO_ROOT / "hub" / "skills" / name / "SKILL.md"
            self.assertTrue(path.is_file(), path)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"))
            self.assertIn(f"name: {name}", text)

    def test_converter_is_stdlib_script(self):
        script = (
            REPO_ROOT
            / "hub"
            / "skills"
            / "confluence-page"
            / "scripts"
            / "md-to-confluence.py"
        )
        self.assertTrue(script.is_file(), script)
        src = script.read_text(encoding="utf-8")
        self.assertNotIn("prd_work_plan", src)
        self.assertIn("def convert(", src)


if __name__ == "__main__":
    unittest.main()
