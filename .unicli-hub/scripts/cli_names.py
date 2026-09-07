"""Canonical CLI names for --target flags."""

from __future__ import annotations

ALIASES = {
    "agy": "antigravity",
    "antigravity": "antigravity",
}


def canonical_cli(name: str | None) -> str | None:
    if name is None:
        return None
    return ALIASES.get(name, name)
