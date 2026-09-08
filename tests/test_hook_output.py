#!/usr/bin/env python3
"""Tests for hook_output.py — per-CLI hook stdout schemas.

Claude Code rejects the legacy top-level `decision` field, so an allow must be
silence and a deny must travel through `hookSpecificOutput.permissionDecision`.
Every other CLI still reads the legacy `permission` shape.
"""

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = ROOT / "hub" / "hooks"
sys.path.insert(0, str(HOOKS))

import hook_output


CLAUDE_PRE = {"hook_event_name": "PreToolUse", "tool_name": "Bash"}
CURSOR_PRE = {"hook_event_name": "preToolUse"}
ANTIGRAVITY = {"toolCall": {"args": {"TargetFile": "CLAUDE.md"}}}


class TestClaudeEvent(unittest.TestCase):
    def test_claude_event_names_are_recognised(self):
        self.assertEqual(hook_output.claude_event(CLAUDE_PRE), "PreToolUse")

    def test_cursor_camel_case_is_not_claude(self):
        self.assertIsNone(hook_output.claude_event(CURSOR_PRE))

    def test_payload_without_event_name_is_not_claude(self):
        self.assertIsNone(hook_output.claude_event(ANTIGRAVITY))

    def test_non_dict_payload(self):
        self.assertIsNone(hook_output.claude_event("not a dict"))


class TestAllowDoc(unittest.TestCase):
    def test_claude_allow_is_silent(self):
        self.assertIsNone(hook_output.allow_doc(CLAUDE_PRE))

    def test_other_cli_allow_keeps_legacy_shape(self):
        self.assertEqual(
            hook_output.allow_doc(CURSOR_PRE),
            {"decision": "allow", "permission": "allow"},
        )

    def test_unknown_caller_is_silent(self):
        self.assertIsNone(hook_output.allow_doc({}))
        self.assertIsNone(hook_output.allow_doc(None))


class TestDenyDoc(unittest.TestCase):
    def test_claude_deny_uses_hook_specific_output(self):
        doc = hook_output.deny_doc(CLAUDE_PRE, "nope")
        self.assertEqual(
            doc,
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "nope",
                }
            },
        )

    def test_claude_deny_never_emits_legacy_decision(self):
        self.assertNotIn("decision", hook_output.deny_doc(CLAUDE_PRE, "nope"))

    def test_claude_non_pretooluse_cannot_refuse(self):
        self.assertIsNone(
            hook_output.deny_doc({"hook_event_name": "PostToolUse"}, "nope")
        )

    def test_other_cli_deny_keeps_legacy_shape(self):
        doc = hook_output.deny_doc(ANTIGRAVITY, "nope")
        self.assertEqual(doc["decision"], "deny")
        self.assertEqual(doc["permission"], "deny")
        self.assertEqual(doc["reason"], "nope")


class TestHookEntryPoints(unittest.TestCase):
    """End-to-end: the bytes the CLI actually reads on stdout."""

    def run_hook(self, name, payload):
        proc = subprocess.run(
            [sys.executable, str(HOOKS / name)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout

    def test_claude_allow_writes_nothing(self):
        for hook in ("pre_tool_use.py", "post_tool_use.py"):
            with self.subTest(hook=hook):
                code, out = self.run_hook(hook, CLAUDE_PRE)
                self.assertEqual(out, "")
                self.assertEqual(code, 0)

    def test_claude_deny_is_schema_valid_and_blocks(self):
        payload = dict(CLAUDE_PRE, tool_input={"file_path": "CLAUDE.md"})
        code, out = self.run_hook("pre_tool_use.py", payload)
        self.assertEqual(code, 2)
        doc = json.loads(out)
        self.assertEqual(
            doc["hookSpecificOutput"]["permissionDecision"], "deny"
        )
        self.assertNotIn("decision", doc)

    def test_other_cli_allow_keeps_legacy_shape(self):
        code, out = self.run_hook("pre_tool_use.py", CURSOR_PRE)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["permission"], "allow")

    def test_unparseable_stdin_writes_nothing(self):
        proc = subprocess.run(
            [sys.executable, str(HOOKS / "pre_tool_use.py")],
            input="not json",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
