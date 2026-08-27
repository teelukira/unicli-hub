#!/usr/bin/env python3
"""Tests for auto_update.py once-per-session update logic."""

import json
import os
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hub" / "hooks"))

import auto_update


class TestSessionAutoUpdate(unittest.TestCase):
    def test_session_cache_and_debounce(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_cache_dir = pathlib.Path(tmpdir)
            temp_cache_file = temp_cache_dir / ".session_cache.json"

            orig_dir = auto_update.CACHE_DIR
            orig_file = auto_update.SESSION_CACHE_FILE
            try:
                auto_update.CACHE_DIR = temp_cache_dir
                auto_update.SESSION_CACHE_FILE = temp_cache_file

                # 1. Initial state: not checked
                self.assertFalse(auto_update.is_session_already_checked("session-123"))

                # 2. Mark session as checked
                auto_update.mark_session_as_checked("session-123")
                self.assertTrue(temp_cache_file.exists())

                # 3. Same session should be marked as checked
                self.assertTrue(auto_update.is_session_already_checked("session-123"))

                # 4. Global debounce should also be active for unspecified session
                self.assertTrue(auto_update.is_session_already_checked(None, debounce_sec=600))

                # 5. Different session should also be covered by global debounce if within debounce_sec
                self.assertTrue(auto_update.is_session_already_checked("session-456", debounce_sec=600))

                # 6. If debounce_sec is 0, a different session is NOT covered unless explicitly checked
                self.assertFalse(auto_update.is_session_already_checked("session-456", debounce_sec=0))
            finally:
                auto_update.CACHE_DIR = orig_dir
                auto_update.SESSION_CACHE_FILE = orig_file

    def test_disable_flag(self):
        os.environ["UNICLI_DISABLE_AUTO_UPDATE"] = "1"
        self.assertTrue(auto_update.is_auto_update_disabled())
        del os.environ["UNICLI_DISABLE_AUTO_UPDATE"]

        os.environ["UNICLI_AUTO_UPDATE"] = "0"
        self.assertTrue(auto_update.is_auto_update_disabled())
        del os.environ["UNICLI_AUTO_UPDATE"]


if __name__ == "__main__":
    unittest.main()
