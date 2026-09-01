#!/usr/bin/env python3
"""Tests for generated_file_guard.py."""

import sys
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hub" / "hooks"))

import generated_file_guard


class TestExtractPath(unittest.TestCase):
    def test_tool_input_file_path(self):
        payload = {"tool_input": {"file_path": "path/to/file.txt"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "path/to/file.txt")

    def test_tool_input_path(self):
        payload = {"tool_input": {"path": "another/path.md"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "another/path.md")

    def test_toolInput_file_path(self):
        payload = {"toolInput": {"file_path": "mixedCase/file.json"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "mixedCase/file.json")

    def test_toolInput_path(self):
        payload = {"toolInput": {"path": "mixedCase/path.yml"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "mixedCase/path.yml")

    def test_args_file_path(self):
        payload = {"args": {"file_path": "args/file.js"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "args/file.js")

    def test_args_path(self):
        payload = {"args": {"path": "args/path.py"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "args/path.py")

    def test_missing_keys(self):
        payload = {"other_key": {"file_path": "some/path.txt"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "")

        payload = {"tool_input": {"other_key": "some/path.txt"}}
        self.assertEqual(generated_file_guard.extract_path(payload), "")

    def test_empty_payload(self):
        self.assertEqual(generated_file_guard.extract_path({}), "")

    def test_non_dict_intermediate_node(self):
        payload = {"tool_input": "not a dict"}
        self.assertEqual(generated_file_guard.extract_path(payload), "")

    def test_non_string_value(self):
        payload = {"tool_input": {"file_path": 123}}
        self.assertEqual(generated_file_guard.extract_path(payload), "")

        payload = {"tool_input": {"file_path": ["a", "b"]}}
        self.assertEqual(generated_file_guard.extract_path(payload), "")

    def test_first_match_wins(self):
        payload = {
            "tool_input": {"file_path": "first.txt"},
            "args": {"path": "second.txt"}
        }
        self.assertEqual(generated_file_guard.extract_path(payload), "first.txt")

if __name__ == "__main__":
    unittest.main()
