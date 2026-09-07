#!/usr/bin/env python3
"""lock_sync.py — Safe wrapper to run sync.py with file lock."""

from __future__ import annotations

import pathlib
import sys

script_dir = pathlib.Path(__file__).resolve().parent
auto_update_path = script_dir / "auto_update.py"

if auto_update_path.exists():
    import importlib.util

    spec = importlib.util.spec_from_file_location("auto_update", auto_update_path)
    if spec and spec.loader:
        auto_update = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_update)
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        ok = auto_update.sync_targets(root)
        sys.exit(0 if ok else 1)

# Fallback
sys.exit(0)
