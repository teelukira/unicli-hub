#!/usr/bin/env python3
"""Smoke test for the confluence-page Markdown converter."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONVERTER = REPO_ROOT / "hub" / "skills" / "confluence-page" / "scripts" / "md-to-confluence.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("md_to_confluence", CONVERTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MdToConfluenceTest(unittest.TestCase):
    def test_table_heading_code_and_plantuml(self):
        conv = load_converter()
        md = """# Title

## Section

| k | v |
| --- | --- |
| a | b |

```python
print(1)
```

```plantuml
@startuml
A --> B : x
@enduml
```
"""
        html = conv.convert(md)
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn('ac:name="toc"', html)
        self.assertIn('<table class="wrapped">', html)
        self.assertIn("<th>k</th>", html)
        self.assertIn('ac:name="code"', html)
        self.assertIn("print(1)", html)
        self.assertIn('ac:name="plantuml"', html)
        self.assertIn("hide stereotype", html)

    def test_cli_writes_file(self):
        conv = load_converter()
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.md"
            dst = Path(tmp) / "out.storage.html"
            src.write_text("# Hi\n\nhello\n", encoding="utf-8")
            # argparse main
            import sys

            argv = sys.argv
            try:
                sys.argv = ["md-to-confluence.py", str(src), str(dst)]
                conv.main()
            finally:
                sys.argv = argv
            out = dst.read_text(encoding="utf-8")
            self.assertIn("<h1>Hi</h1>", out)
            self.assertIn("<p>hello</p>", out)


if __name__ == "__main__":
    unittest.main()
