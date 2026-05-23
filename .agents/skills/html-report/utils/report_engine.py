#!/usr/bin/env python3
"""HTML report engine — turns a compact JSON spec into a self-contained report.

Usage:
    python hub/skills/html-report/utils/report_engine.py spec.json -o out.html
    python hub/skills/html-report/utils/report_engine.py spec.json --check
    python hub/skills/html-report/utils/report_engine.py spec.json -o out.html --embed-assets

The author writes only the JSON spec; this engine expands it into verbose,
styled, self-contained HTML so report markup is never hand-written. See
hub/skills/html-report/utils/README.md for the full spec schema.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import urllib.request
from pathlib import Path

try:  # package import (when imported as a package)
    from . import inline, theme
except ImportError:  # script import (python hub/skills/html-report/utils/report_engine.py)
    import inline
    import theme

COMPONENT_TYPES = {
    "text", "stat_grid", "table", "progress_list", "badge", "legend",
    "status_grid", "callout", "code_block", "mermaid", "details",
    "image_grid", "raw_html",
}
STAT_COLORS = {"green", "red", "yellow", "blue", "gray", "purple"}
FILL_COLORS = {"green", "red", "yellow", "blue"}
CALLOUT_SEVERITIES = {"info", "warn", "error", "success", "gap"}
STATUS_KINDS = {"up", "down", "warn"}
NAMED_COLORS = {
    "green": "#2f7d4f", "red": "#bf3b2f", "amber": "#b07514",
    "blue": "#2b6cb0", "gray": "#5a6066", "purple": "#7b4ea8",
    "orange": "#9a571c", "resource": "#1d5e8a", "catalog": "#2c6e4a",
    "geo": "#8a6d12", "ipam": "#a23b32", "zone": "#9a571c",
    "party": "#6b4ba0", "logical": "#4a4f59",
}


class SpecError(Exception):
    """Raised when a report spec cannot be rendered."""


def _load_mermaid_js() -> str:
    """Return Mermaid JS, downloading once and caching locally for offline use."""
    cache = theme.MERMAID_CACHE
    if cache.exists():
        return cache.read_text("utf-8")
    print(f"  downloading Mermaid JS → {cache.name} ...", file=sys.stderr, flush=True)
    req = urllib.request.Request(
        theme.MERMAID_CDN,
        headers={"Accept-Encoding": "identity", "User-Agent": "report-engine/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    cache.write_text(data, "utf-8")
    print(f"  cached {len(data):,} bytes", file=sys.stderr, flush=True)
    return data


def _color_hex(value: str) -> str:
    """Resolve a named or literal hex color to a safe hex string."""
    if not value:
        return NAMED_COLORS["gray"]
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]
    v = value.strip()
    if v.startswith("#") and 4 <= len(v) <= 7:
        body = v[1:]
        if all(c in "0123456789abcdefABCDEF" for c in body):
            return v
    return NAMED_COLORS["gray"]


class ReportRenderer:
    """Renders a parsed report spec dict to a single self-contained HTML string."""

    def __init__(self, spec: dict, embed_assets: bool = False, base_dir=None):
        if not isinstance(spec, dict):
            raise SpecError("spec root must be a JSON object")
        self.spec = spec
        self.embed_assets = embed_assets
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._dispatch = {
            "text": self._render_text,
            "stat_grid": self._render_stat_grid,
            "table": self._render_table,
            "progress_list": self._render_progress_list,
            "badge": self._render_badge,
            "legend": self._render_legend,
            "status_grid": self._render_status_grid,
            "callout": self._render_callout,
            "code_block": self._render_code_block,
            "mermaid": self._render_mermaid,
            "details": self._render_details,
            "image_grid": self._render_image_grid,
            "raw_html": self._render_raw_html,
        }

    # -- public ------------------------------------------------------------
    def render(self) -> str:
        sections = self.spec.get("sections") or []
        self._number_sections(sections)
        lang = inline.plain(self.spec.get("lang", "en"))
        title = inline.plain(self.spec.get("title", "Report"))
        body = [
            '<div class="rpt">',
            self._render_header(),
            self._render_toc(sections),
        ]
        body += [self._render_section(s) for s in sections]
        body.append(self._render_footer())
        body.append("</div>")
        if self._has_mermaid(self.spec):
            body.append("<script>%s</script>" % _load_mermaid_js())
            body.append("<script>%s</script>" % theme.MERMAID_INIT)
            body.append("<script>%s</script>" % theme.MERMAID_ENHANCE_JS)
        style = theme.accent_root(self.spec.get("accent", theme.DEFAULT_ACCENT))
        return (
            "<!DOCTYPE html>\n"
            '<html lang="%s">\n<head>\n' % lang
            + '<meta charset="utf-8">\n'
            + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + "<title>%s</title>\n" % title
            + "<style>\n%s\n%s</style>\n" % (style, theme.THEME_CSS)
            + "</head>\n<body>\n"
            + "\n".join(body)
            + "\n</body>\n</html>\n"
        )

    # -- structure ---------------------------------------------------------
    def _number_sections(self, sections: list) -> None:
        for i, sec in enumerate(sections, 1):
            if not isinstance(sec, dict):
                raise SpecError("section #%d must be an object" % i)
            sec.setdefault("_index", sec.get("index", str(i)))
            sec.setdefault("_id", sec.get("id", "sec-%d" % i))
            for j, sub in enumerate(sec.get("subsections") or [], 1):
                if not isinstance(sub, dict):
                    raise SpecError("subsection in %s must be an object" % sec["_id"])
                sub.setdefault("_id", sub.get("id", "%s-%d" % (sec["_id"], j)))

    def _render_header(self) -> str:
        out = ['<header class="rpt-header">']
        kicker = self.spec.get("kicker")
        if kicker:
            out.append('<div class="rpt-kicker">%s</div>' % inline.plain(kicker))
        out.append('<h1 class="rpt-title">%s</h1>'
                   % inline.render(self.spec.get("title", "Report")))
        subtitle = self.spec.get("subtitle")
        if subtitle:
            out.append('<p class="rpt-subtitle">%s</p>' % inline.render(subtitle))
        meta = self.spec.get("metadata") or {}
        if meta:
            out.append('<div class="rpt-meta">')
            for key, val in meta.items():
                out.append(
                    '<div class="rpt-meta-item">'
                    '<span class="rpt-meta-key">%s</span>'
                    '<span class="rpt-meta-val">%s</span></div>'
                    % (inline.plain(key), inline.render(val))
                )
            out.append("</div>")
        out.append("</header>")
        return "\n".join(out)

    def _render_toc(self, sections: list) -> str:
        toc = self.spec.get("toc")
        if not toc:
            return ""
        variant = toc.get("variant", "sticky-horizontal")
        entries = toc.get("entries")
        if entries is None and toc.get("auto", True):
            entries = [{"id": s["_id"], "title": s.get("title", ""),
                        "index": s["_index"]} for s in sections]
        entries = entries or []
        links = []
        for e in entries:
            idx = e.get("index", "")
            idx_html = ('<span class="toc-index">%s</span>' % inline.plain(idx)
                        if idx != "" else "")
            links.append('<a class="toc-link" href="#%s">%s%s</a>'
                         % (inline.plain(e.get("id", "")), idx_html,
                            inline.plain(e.get("title", ""))))
        if variant == "card-vertical":
            title = inline.plain(toc.get("title", "Contents"))
            items = "".join("<li>%s</li>" % lk for lk in links)
            return ('<nav class="toc--vertical">'
                    '<div class="toc-title">%s</div><ol>%s</ol></nav>'
                    % (title, items))
        return ('<nav class="toc--horizontal">%s</nav>' % "".join(links))

    def _render_section(self, sec: dict) -> str:
        out = ['<section class="section" id="%s">' % inline.plain(sec["_id"])]
        out.append('<div class="section-head">')
        out.append('<span class="section-index">%s</span>'
                   % inline.plain(sec.get("_index", "")))
        out.append('<h2 class="section-title">%s</h2>'
                   % inline.render(sec.get("title", "")))
        status = sec.get("status")
        if status:
            kind = status.get("kind", "info")
            out.append('<span class="section-status">'
                       '<span class="badge %s">%s</span></span>'
                       % (inline.plain(kind), inline.render(status.get("label", ""))))
        out.append("</div>")
        out.append(self._render_components(sec.get("components") or []))
        for sub in sec.get("subsections") or []:
            out.append('<div class="subsection" id="%s">' % inline.plain(sub["_id"]))
            out.append('<h3 class="subsection-title">%s</h3>'
                       % inline.render(sub.get("title", "")))
            out.append(self._render_components(sub.get("components") or []))
            out.append("</div>")
        out.append("</section>")
        return "\n".join(p for p in out if p)

    def _render_footer(self) -> str:
        footer = self.spec.get("footer")
        if footer is None:
            footer = "Generated by hub/skills/html-report/utils/report_engine.py"
        items = footer if isinstance(footer, list) else [footer]
        spans = "".join("<span>%s</span>" % inline.render(x) for x in items)
        return '<footer class="rpt-footer">%s</footer>' % spans

    # -- component dispatch -----------------------------------------------
    def _render_components(self, comps: list) -> str:
        return "\n".join(self._render_component(c) for c in comps)

    def _render_component(self, comp) -> str:
        if not isinstance(comp, dict) or "type" not in comp:
            raise SpecError("each component must be an object with a 'type'")
        ctype = comp["type"]
        handler = self._dispatch.get(ctype)
        if handler is None:
            raise SpecError("unknown component type: %r" % ctype)
        return handler(comp)

    # -- components --------------------------------------------------------
    def _render_text(self, c: dict) -> str:
        value = c.get("value", "")
        paras = value if isinstance(value, list) else [value]
        return "\n".join('<p class="text">%s</p>' % inline.render(p) for p in paras)

    def _render_stat_grid(self, c: dict) -> str:
        cards = []
        for card in c.get("cards") or []:
            color = card.get("color")
            cls = "stat-card is-%s" % color if color in STAT_COLORS else "stat-card"
            cards.append(
                '<div class="%s"><div class="stat-value">%s</div>'
                '<div class="stat-label">%s</div></div>'
                % (cls, inline.render(card.get("value", "")),
                   inline.render(card.get("label", "")))
            )
        return '<div class="stat-grid">%s</div>' % "".join(cards)

    def _render_table(self, c: dict) -> str:
        columns = c.get("columns") or []
        if not columns:
            raise SpecError("table requires non-empty 'columns'")
        col_align = {col["key"]: col.get("align") for col in columns
                     if isinstance(col, dict) and "key" in col}
        ncols = len(columns)
        head = "".join("<th>%s</th>" % inline.render(col.get("label", ""))
                       for col in columns)
        rows_html = []
        for row in c.get("rows") or []:
            if row.get("kind") == "group":
                rows_html.append(
                    '<tr class="group"><td class="group-cell" colspan="%d">%s</td></tr>'
                    % (ncols, inline.render(row.get("label", "")))
                )
                continue
            cells = row.get("cells") or {}
            tds = []
            for col in columns:
                key = col.get("key")
                tds.append(self._render_cell(cells.get(key), col_align.get(key)))
            rows_html.append("<tr>%s</tr>" % "".join(tds))
        return ('<div class="table-wrap"><table class="rpt-table">'
                '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % (head, "".join(rows_html)))

    def _render_cell(self, value, col_align) -> str:
        align = col_align
        if isinstance(value, dict):
            text = value.get("text", "")
            color = value.get("color")
            align = value.get("align", col_align)
            content = inline.render(text)
            if color in inline.COLORS:
                content = '<span class="c-%s">%s</span>' % (color, content)
        else:
            content = inline.render(value)
        cls = ""
        if align in ("center", "right"):
            cls = ' class="cell--%s"' % align
        return "<td%s>%s</td>" % (cls, content)

    def _render_progress_list(self, c: dict) -> str:
        items = []
        for it in c.get("items") or []:
            try:
                pct = max(0.0, min(100.0, float(it.get("value", 0))))
            except (TypeError, ValueError):
                pct = 0.0
            color = it.get("color")
            fill_cls = "progress-fill is-%s" % color if color in FILL_COLORS \
                else "progress-fill"
            text = it.get("text", "%g%%" % pct)
            items.append(
                '<div class="progress-item"><div class="progress-label">'
                '<span>%s</span><span class="progress-text">%s</span></div>'
                '<div class="progress-track"><div class="%s" style="width:%g%%">'
                "</div></div></div>"
                % (inline.render(it.get("label", "")), inline.render(text),
                   fill_cls, pct)
            )
        return '<div class="progress-list">%s</div>' % "".join(items)

    def _render_badge(self, c: dict) -> str:
        badges = []
        for it in c.get("items") or []:
            kind = it.get("kind", "info")
            if kind not in inline.BADGE_KINDS:
                kind = "info"
            badges.append('<span class="badge %s">%s</span>'
                          % (kind, inline.render(it.get("text", ""))))
        return '<div class="badge-row">%s</div>' % "".join(badges)

    def _render_legend(self, c: dict) -> str:
        items = []
        for it in c.get("items") or []:
            hexc = _color_hex(it.get("color", "gray"))
            items.append(
                '<span class="legend-item">'
                '<span class="legend-dot" style="background:%s"></span>%s</span>'
                % (hexc, inline.render(it.get("label", "")))
            )
        return '<div class="legend">%s</div>' % "".join(items)

    def _render_status_grid(self, c: dict) -> str:
        items = []
        for it in c.get("items") or []:
            status = it.get("status", "")
            cls = "status-item is-%s" % status if status in STATUS_KINDS \
                else "status-item"
            meta = it.get("meta")
            meta_html = ('<div class="status-meta">%s</div>' % inline.render(meta)
                         if meta else "")
            items.append(
                '<div class="%s"><span class="status-dot"></span><div>'
                '<div class="status-name">%s</div>%s</div></div>'
                % (cls, inline.render(it.get("name", "")), meta_html)
            )
        return '<div class="status-grid">%s</div>' % "".join(items)

    def _render_callout(self, c: dict) -> str:
        severity = c.get("severity", "info")
        if severity not in CALLOUT_SEVERITIES:
            severity = "info"
        label = c.get("label", severity.upper())
        out = ['<div class="callout callout--%s">' % severity]
        out.append('<div class="callout-label">%s</div>' % inline.plain(label))
        if c.get("title"):
            out.append('<div class="callout-title">%s</div>'
                       % inline.render(c["title"]))
        if c.get("body"):
            out.append('<div class="callout-body">%s</div>'
                       % inline.render(c["body"]))
        out.append("</div>")
        return "".join(out)

    def _render_code_block(self, c: dict) -> str:
        lang = c.get("language", "")
        lang_html = ('<span class="code-lang">%s</span>' % inline.plain(lang)
                     if lang else "")
        return ('<div class="code-block">%s<pre>%s</pre></div>'
                % (lang_html, inline.plain(c.get("code", ""))))

    def _render_mermaid(self, c: dict) -> str:
        diagram = str(c.get("diagram", ""))
        low = diagram.lower()
        if "<script" in low or "</script" in low:
            raise SpecError("mermaid diagram must not contain <script>")
        return ('<div class="mermaid-wrap"><div class="mermaid">%s</div>'
                '<noscript><div class="mermaid-fallback">'
                "[diagram requires JavaScript]</div></noscript></div>" % diagram)

    def _render_details(self, c: dict) -> str:
        open_attr = " open" if c.get("open") else ""
        return ('<details class="rpt-details"%s><summary>%s</summary>'
                '<div class="rpt-details-body">%s</div></details>'
                % (open_attr, inline.render(c.get("summary", "Details")),
                   self._render_components(c.get("components") or [])))

    def _render_image_grid(self, c: dict) -> str:
        cards = []
        for img in c.get("images") or []:
            src = self._asset_src(img.get("src", ""))
            caption = img.get("caption")
            cap_html = ('<div class="image-caption">%s</div>'
                        % inline.render(caption) if caption else "")
            cards.append('<figure class="image-card"><img src="%s" alt="%s">%s</figure>'
                         % (inline.plain(src),
                            inline.plain(caption or img.get("src", "")), cap_html))
        return '<div class="image-grid">%s</div>' % "".join(cards)

    def _render_raw_html(self, c: dict) -> str:
        return str(c.get("html", ""))

    # -- helpers -----------------------------------------------------------
    def _asset_src(self, src: str) -> str:
        if not self.embed_assets or src.startswith(("http://", "https://", "data:")):
            return src
        path = self.base_dir / src
        if path.is_file():
            mime = mimetypes.guess_type(str(path))[0] or "image/png"
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            return "data:%s;base64,%s" % (mime, data)
        return src

    def _has_mermaid(self, node) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "mermaid":
                return True
            return any(self._has_mermaid(v) for v in node.values())
        if isinstance(node, list):
            return any(self._has_mermaid(v) for v in node)
        return False


# --- validation ------------------------------------------------------------
def validate(spec) -> list[str]:
    """Return a list of spec problems (empty list = valid)."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["spec root must be a JSON object"]
    if not spec.get("title"):
        errors.append("spec is missing 'title'")
    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("spec needs a non-empty 'sections' list")
        return errors
    for i, sec in enumerate(sections, 1):
        where = "section #%d" % i
        if not isinstance(sec, dict):
            errors.append("%s must be an object" % where)
            continue
        if not sec.get("title"):
            errors.append("%s is missing 'title'" % where)
        for comp in sec.get("components") or []:
            _validate_component(comp, where, errors)
        for j, sub in enumerate(sec.get("subsections") or [], 1):
            subwhere = "%s subsection #%d" % (where, j)
            if not isinstance(sub, dict):
                errors.append("%s must be an object" % subwhere)
                continue
            for comp in sub.get("components") or []:
                _validate_component(comp, subwhere, errors)
    return errors


def _validate_component(comp, where: str, errors: list) -> None:
    if not isinstance(comp, dict) or "type" not in comp:
        errors.append("%s: component must be an object with 'type'" % where)
        return
    ctype = comp["type"]
    if ctype not in COMPONENT_TYPES:
        errors.append("%s: unknown component type %r" % (where, ctype))
        return
    if ctype == "table":
        cols = comp.get("columns")
        if not isinstance(cols, list) or not cols:
            errors.append("%s: table needs non-empty 'columns'" % where)
            return
        keys = {col.get("key") for col in cols if isinstance(col, dict)}
        if None in keys:
            errors.append("%s: every table column needs a 'key'" % where)
        for r, row in enumerate(comp.get("rows") or [], 1):
            if isinstance(row, dict) and row.get("kind") != "group":
                extra = set((row.get("cells") or {}).keys()) - keys
                if extra:
                    errors.append("%s: table row #%d has unknown cell keys %s"
                                  % (where, r, sorted(extra)))
    elif ctype == "callout":
        sev = comp.get("severity", "info")
        if sev not in CALLOUT_SEVERITIES:
            errors.append("%s: callout severity %r is not one of %s"
                          % (where, sev, sorted(CALLOUT_SEVERITIES)))
    elif ctype == "mermaid":
        if not comp.get("diagram"):
            errors.append("%s: mermaid component needs a 'diagram'" % where)
    elif ctype == "details":
        for sub in comp.get("components") or []:
            _validate_component(sub, where + " > details", errors)


# --- CLI --------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a JSON spec to HTML.")
    parser.add_argument("spec", help="path to the JSON report spec")
    parser.add_argument("-o", "--output", help="output HTML file path")
    parser.add_argument("--embed-assets", action="store_true",
                        help="base64-inline local images for a single-file artifact")
    parser.add_argument("--check", action="store_true",
                        help="validate the spec and exit (no output written)")
    args = parser.parse_args(argv)

    spec_path = Path(args.spec)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("error: spec file not found: %s" % spec_path, file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print("error: invalid JSON in %s: %s" % (spec_path, exc), file=sys.stderr)
        return 1

    if args.check:
        errors = validate(spec)
        if errors:
            print("SPEC INVALID (%d problem(s)):" % len(errors), file=sys.stderr)
            for e in errors:
                print("  - %s" % e, file=sys.stderr)
            return 1
        print("spec OK: %s" % spec_path)
        return 0

    if not args.output:
        print("error: -o/--output is required unless --check is used",
              file=sys.stderr)
        return 1

    try:
        html_out = ReportRenderer(
            spec, embed_assets=args.embed_assets, base_dir=spec_path.resolve().parent
        ).render()
    except SpecError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print("wrote %s (%d bytes)" % (out_path, len(html_out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
