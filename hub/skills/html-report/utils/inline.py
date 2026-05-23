"""Inline mini-markup parser for the HTML report engine.

Lets a spec author keep table cells / text / list items as compact
one-line strings while still producing rich HTML. The whole input is
HTML-escaped first; only the whitelisted markers below re-introduce tags:

    `code`            -> <code>
    **bold**          -> <strong>
    ~small~           -> <small>
    [badge:KIND]x[/]  -> <span class="badge KIND">   (KIND whitelisted)
    [c:COLOR]x[/]     -> <span class="c-COLOR">       (COLOR whitelisted)
    [link:#id]x[/]    -> <a href="#id">               (anchor hrefs only)
    \\n               -> <br>

No marker can introduce a tag outside this set, so spec strings are safe
even when they originate from extracted/legacy data.
"""

from __future__ import annotations

import html
import re

BADGE_KINDS = {
    "pass", "fail", "warn", "info", "success", "error", "skip", "new", "gap",
    "resource", "catalog", "geo", "ipam", "zone", "party", "logical",
}
COLORS = {"red", "green", "amber", "blue", "gray"}

_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_SMALL_RE = re.compile(r"~([^~]+)~")
_BADGE_RE = re.compile(r"\[badge:([a-z]+)\](.+?)\[/\]")
_COLOR_RE = re.compile(r"\[c:([a-z]+)\](.+?)\[/\]")
_LINK_RE = re.compile(r"\[link:(#[\w-]+)\](.+?)\[/\]")
_SENTINEL = "\x00"
_RESTORE_RE = re.compile(_SENTINEL + r"(\d+)" + _SENTINEL)


def render(text) -> str:
    """Render a spec string to an HTML-safe fragment with inline markup."""
    if text is None:
        return ""
    raw = html.escape(str(text), quote=False)

    # Protect code spans so their contents are not re-parsed for **/~/[..].
    stash: list[str] = []

    def _stash_code(m: "re.Match[str]") -> str:
        stash.append("<code>" + m.group(1) + "</code>")
        return _SENTINEL + str(len(stash) - 1) + _SENTINEL

    out = _CODE_RE.sub(_stash_code, raw)
    out = _BOLD_RE.sub(r"<strong>\1</strong>", out)

    def _badge(m: "re.Match[str]") -> str:
        kind = m.group(1) if m.group(1) in BADGE_KINDS else "info"
        return '<span class="badge ' + kind + '">' + m.group(2) + "</span>"

    def _color(m: "re.Match[str]") -> str:
        if m.group(1) not in COLORS:
            return m.group(2)
        return '<span class="c-' + m.group(1) + '">' + m.group(2) + "</span>"

    out = _BADGE_RE.sub(_badge, out)
    out = _COLOR_RE.sub(_color, out)
    out = _LINK_RE.sub(r'<a href="\1">\2</a>', out)
    out = _SMALL_RE.sub(r"<small>\1</small>", out)
    out = out.replace("\n", "<br>")

    return _RESTORE_RE.sub(lambda m: stash[int(m.group(1))], out)


def plain(text) -> str:
    """Escape a string with no markup interpretation (attributes, captions)."""
    return html.escape("" if text is None else str(text), quote=True)
