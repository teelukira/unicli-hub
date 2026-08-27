#!/usr/bin/env python3
"""Tests for generated_file_guard.py."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hub" / "hooks"))

import generated_file_guard


class TestNormalize(unittest.TestCase):
    def test_normalize_empty_path(self):
        self.assertEqual(generated_file_guard.normalize(""), "")
        self.assertEqual(generated_file_guard.normalize(None), "")

    def test_normalize_without_marker(self):
        self.assertEqual(generated_file_guard.normalize("some/path/file.txt"), "some/path/file.txt")
        self.assertEqual(generated_file_guard.normalize("/some/path/file.txt"), "some/path/file.txt")
        self.assertEqual(generated_file_guard.normalize("///some/path/file.txt"), "some/path/file.txt")

    def test_normalize_with_marker(self):
        self.assertEqual(generated_file_guard.normalize("/home/user/project/unicli-hub/some/path/file.txt"), "some/path/file.txt")
        self.assertEqual(generated_file_guard.normalize("/unicli-hub/some/path/file.txt"), "some/path/file.txt")
        self.assertEqual(generated_file_guard.normalize("path/to/unicli-hub/file.txt"), "file.txt")

if __name__ == "__main__":
    unittest.main()
