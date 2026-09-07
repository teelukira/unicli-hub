"""Absolute Python interpreter for generated launcher commands.

Generated targets are gitignored and re-rendered per machine, so a launcher
only has to run where it was rendered. Embedding the absolute interpreter
avoids guessing a name that does not exist on the host: `python` is absent on
macOS and most Linux, `python3` is absent on Windows.
"""

from __future__ import annotations

import shutil
import sys


def python_interpreter() -> str:
    return (
        sys.executable
        or shutil.which("python3")
        or shutil.which("python")
        or "python3"
    )
