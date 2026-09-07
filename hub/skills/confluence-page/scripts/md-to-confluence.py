#!/usr/bin/env python3
"""Markdown -> Confluence storage format converter.

Stdlib only. Output is the body for mcp-atlassian confluence_update_page /
confluence_create_page with content_format="storage".

Usage:
  python hub/skills/confluence-page/scripts/md-to-confluence.py INPUT.md OUTPUT.storage.html

Supports: headings h1-h6, tables (wrapped), nested lists, fenced code (code
macro), plantuml/mermaid (plantuml macro; mermaid is converted), blockquotes
(panel), hr, inline code/bold/links, TOC macro after the first h1.
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^-\s+(.*)$")
ORDERED_RE = re.compile(r"^\d+\.\s+(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")


def inline(value: str) -> str:
    placeholders: list[str] = []

    def save_code(match: re.Match[str]) -> str:
        placeholders.append(f"<code>{html.escape(match.group(1))}</code>")
        return f"@@INLINE{len(placeholders) - 1}@@"

    value = re.sub(r"`([^`]+)`", save_code, value)
    escaped = html.escape(value, quote=False)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)

    # 마크다운 링크 [텍스트](URL) 을 먼저 처리해 placeholder 로 빼둔다.
    # 아래 bare URL autolink 가 링크 안의 URL 을 다시 감싸 <a href="...)">...)</a> 로
    # 깨뜨리는 것을 막기 위함이다.
    def save_link(match: re.Match[str]) -> str:
        label = match.group(1)
        href = html.escape(match.group(2), quote=True)
        placeholders.append(f'<a href="{href}">{label}</a>')
        return f"@@INLINE{len(placeholders) - 1}@@"

    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", save_link, escaped)

    escaped = re.sub(
        r"(https?://[^\s<]+)",
        lambda match: f'<a href="{html.escape(match.group(1), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    for index, replacement in enumerate(placeholders):
        escaped = escaped.replace(f"@@INLINE{index}@@", replacement)
    return escaped


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def clean_mermaid_label(lbl: str) -> str:
    if not lbl:
        return ""
    lbl = lbl.strip().strip("'\"[]()")
    return (
        lbl.replace("<br/>", "\n")
        .replace("<br>", "\n")
        .replace('"', "")
        .replace("'", "")
    )


def mermaid_to_plantuml(code: str) -> str:
    lines = code.strip().splitlines()
    if not lines:
        return "@startuml\nhide stereotype\n@enduml"

    puml = [
        "@startuml",
        "hide stereotype",
        "skinparam backgroundColor white",
        "skinparam defaultFontSize 12",
        "skinparam defaultTextAlignment center",
        "skinparam packageStyle rectangle",
    ]

    declared_nodes: set[str] = set()
    node_defs: list[str] = []
    edges: list[str] = []
    subgraph_stack: list[str] = []

    def declare_node(nid: str, lbl: str, is_db: bool = False) -> None:
        if nid in declared_nodes:
            return
        declared_nodes.add(nid)
        shape = "database" if is_db else "rectangle"
        lbl_c = clean_mermaid_label(lbl)
        if "\n" in lbl_c:
            node_defs.append(f"{shape} {nid} [\n{lbl_c}\n]")
        elif lbl_c:
            node_defs.append(f'{shape} "{lbl_c}" as {nid}')
        else:
            node_defs.append(f"{shape} {nid}")

    for line in lines:
        s = line.strip()
        if (
            not s
            or s.startswith("%%")
            or s.startswith("flowchart")
            or s.startswith("graph")
            or s.startswith("direction")
            or s.startswith("classDef")
            or s.startswith("style")
        ):
            continue

        if s.startswith("subgraph"):
            m = re.match(r"^subgraph\s+([\w\d_-]+)(?:\s+\[?\"?(.*?)\"?\]?)?", s)
            if m:
                sg_id = m.group(1)
                title = m.group(2) or sg_id
                title = clean_mermaid_label(title).replace("\n", " ")
                node_defs.append(f'package "{title}" as {sg_id} {{')
                subgraph_stack.append(sg_id)
            continue

        if s == "end":
            if subgraph_stack:
                subgraph_stack.pop()
                node_defs.append("}")
            continue

        # Check relationship line
        if any(arr in s for arr in ["<-->", "<==>", "==>", "-.->", "-->", "->"]):
            label = ""
            pipe_m = re.search(r"\|\"?(.*?)\"?\|", s)
            if pipe_m:
                label = pipe_m.group(1)
                s = s.replace(pipe_m.group(0), "")
            else:
                quote_m = re.search(r"\"(.*?)\"", s)
                if quote_m:
                    label = quote_m.group(1)
                    s = s.replace(f'"{label}"', "")

            m_arrow = re.search(
                r"(\S+.*?)\s+(<==>|<-->|<==\s*==>|==>|-\.->|-->|->)\s+(\S+.*)", s
            )
            if m_arrow:
                src_raw, arrow, dst_raw = m_arrow.groups()

                def parse_endpoint(raw: str) -> str:
                    raw = raw.strip()
                    m_n = re.match(r"^([\w\d_-]+)\[\"?(.*?)\"?\]$", raw)
                    if m_n:
                        nid = m_n.group(1)
                        nlbl = m_n.group(2)
                        declare_node(nid, nlbl, "[(" in raw or "DB" in nid)
                        return nid
                    m_id = re.match(r"^([\w\d_-]+)", raw)
                    return m_id.group(1) if m_id else raw

                src_id = parse_endpoint(src_raw)
                dst_id = parse_endpoint(dst_raw)

                puml_arrow = "-->"
                if "<" in arrow:
                    puml_arrow = "<-->"
                elif "." in arrow:
                    puml_arrow = "..>"

                lbl_clean = clean_mermaid_label(label).replace("\n", " / ") if label else ""
                lbl_str = f" : {lbl_clean}" if lbl_clean else ""
                edges.append(f"{src_id} {puml_arrow} {dst_id}{lbl_str}")
            continue

        # Simple node definition: Id["Label"] or Id[("Label")]
        m_node = re.match(r"^([\w\d_-]+)\[\"?(.*?)\"?\]$", s)
        if m_node:
            nid = m_node.group(1)
            nlbl = m_node.group(2)
            declare_node(nid, nlbl, "[(" in s or ")]" in s or "DB" in nid)

    while subgraph_stack:
        subgraph_stack.pop()
        node_defs.append("}")

    puml.extend(node_defs)
    puml.extend(edges)
    puml.append("@enduml")
    return "\n".join(puml)


def code_macro(language: str, body: str) -> str:
    safe_body = body.replace("]]>", "]]]]><![CDATA[>")
    lang_lower = (language or "text").lower()

    if lang_lower in ["plantuml", "puml"]:
        if "hide stereotype" not in safe_body:
            safe_body = safe_body.replace("@startuml", "@startuml\nhide stereotype")
        return (
            '<ac:structured-macro ac:name="plantuml" ac:schema-version="1">'
            '<ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{safe_body}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )
    elif lang_lower == "mermaid":
        converted_puml = mermaid_to_plantuml(body).replace("]]>", "]]]]><![CDATA[>")
        return (
            '<ac:structured-macro ac:name="plantuml" ac:schema-version="1">'
            '<ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{converted_puml}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )
    else:
        return (
            '<ac:structured-macro ac:name="code" ac:schema-version="1">'
            f'<ac:parameter ac:name="language">{html.escape(lang_lower)}</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{safe_body}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )


def warning_panel(body_lines: list[str]) -> str:
    full_text = "\n".join(body_lines).strip()
    panel_type = "info"
    title = "요약"

    if full_text.startswith("[!NOTE]"):
        panel_type = "info"
        title = "NOTE"
        full_text = full_text[7:].strip()
    elif full_text.startswith("[!TIP]") or full_text.startswith("[!SUCCESS]"):
        panel_type = "success"
        title = "TIP"
        full_text = full_text[6:].strip()
    elif full_text.startswith("[!WARNING]") or full_text.startswith("[!IMPORTANT]"):
        panel_type = "warning"
        title = "WARNING"
        full_text = full_text[10:].strip()
    elif full_text.startswith("[!CAUTION]") or full_text.startswith("[!ERROR]"):
        panel_type = "error"
        title = "CAUTION"
        full_text = full_text[10:].strip()

    body = " ".join(line.strip() for line in full_text.splitlines() if line.strip())
    return (
        '<ac:structured-macro ac:name="panel" ac:schema-version="1">'
        f'<ac:parameter ac:name="title">{html.escape(title)}</ac:parameter>'
        f'<ac:parameter ac:name="panelType">{panel_type}</ac:parameter>'
        f"<ac:rich-text-body><p>{inline(body)}</p></ac:rich-text-body>"
        "</ac:structured-macro>"
    )


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def render_list(entries: list[tuple[int, str, str]]) -> str:
    """(깊이, 태그, 내용) 목록을 중첩 <ul>/<ol> 로 렌더링한다.

    평탄한 목록을 트리로 세운 뒤 재귀 렌더링한다. 하위 목록은 부모 <li> 안에 들어간다
    (</li><ul> 형태는 유효하지 않은 HTML 이라 Confluence 가 정규화하거나 거부할 수 있다).
    """
    # (깊이, 태그, 내용) -> 트리 노드 {tag, text, children}
    root: list[dict] = []
    path: list[dict] = []  # 깊이별 현재 노드

    for depth, tag, item in entries:
        node = {"tag": tag, "text": item, "children": []}
        depth = min(depth, len(path))  # 건너뛴 깊이는 한 단계로 눌러 받는다
        if depth == 0:
            root.append(node)
            path = [node]
        else:
            path[depth - 1]["children"].append(node)
            path = path[:depth] + [node]

    def render(nodes: list[dict]) -> str:
        if not nodes:
            return ""
        tag = nodes[0]["tag"]
        parts = [f"<{tag}>"]
        for n in nodes:
            parts.append(f"<li>{inline(n['text'])}")
            if n["children"]:
                parts.append(render(n["children"]))
            parts.append("</li>")
        parts.append(f"</{tag}>")
        return "".join(parts)

    return render(root)


def starts_block(line: str, lines: list[str], index: int) -> bool:
    """이 줄이 새 블록(목록·제목·표·코드펜스·인용·수평선)을 시작하는가."""
    if line.startswith(("#", ">", "```")):
        return True
    if line in {"---", "***", "___"}:
        return True
    if BULLET_RE.match(line) or ORDERED_RE.match(line):
        return True
    if (
        "|" in line
        and index + 1 < len(lines)
        and TABLE_SEPARATOR_RE.match(lines[index + 1].strip())
    ):
        return True
    return False


def convert(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    toc_added = False

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip() or "text"
            index += 1
            body: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                body.append(lines[index])
                index += 1
            if index >= len(lines):
                raise ValueError("Unterminated fenced code block")
            output.append(code_macro(language, "\n".join(body)))
            index += 1
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            level = min(len(heading.group(1)), 6)
            output.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            if level == 1 and not toc_added:
                output.append('<ac:structured-macro ac:name="toc" ac:schema-version="1"/>')
                toc_added = True
            index += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            output.append(warning_panel(quote_lines))
            continue

        if stripped in {"---", "***", "___"}:
            output.append("<hr/>")
            index += 1
            continue

        if (
            "|" in stripped
            and index + 1 < len(lines)
            and TABLE_SEPARATOR_RE.match(lines[index + 1].strip())
        ):
            headers = split_table_row(stripped)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            table = ['<table class="wrapped"><tbody><tr>']
            table.extend(f"<th>{inline(cell)}</th>" for cell in headers)
            table.append("</tr>")
            for row in rows:
                normalized = row + [""] * max(0, len(headers) - len(row))
                table.append("<tr>")
                table.extend(f"<td>{inline(cell)}</td>" for cell in normalized[: len(headers)])
                table.append("</tr>")
            table.append("</tbody></table>")
            output.append("".join(table))
            continue

        # 목록. 두 가지를 처리한다.
        #  1) 줄바꿈된 항목 이어 붙이기 — 안 하면 Confluence 에서 <li> 와 별도 <p> 로 쪼개진다.
        #  2) 들여쓰기 중첩 — 안 하면 하위 항목이 형제로 평탄화돼 계층이 사라진다.
        if BULLET_RE.match(stripped) or ORDERED_RE.match(stripped):
            entries: list[tuple[int, str, str]] = []  # (깊이, 태그, 내용)
            base_indent = indent_of(lines[index])
            while index < len(lines):
                raw = lines[index]
                s = raw.strip()
                if not s:
                    break
                bm, om = BULLET_RE.match(s), ORDERED_RE.match(s)
                if not (bm or om):
                    break
                cur_indent = indent_of(raw)
                if cur_indent < base_indent:
                    break
                depth = (cur_indent - base_indent) // 2
                tag = "ul" if bm else "ol"
                item = (bm or om).group(1)
                index += 1
                while index < len(lines):
                    nxt = lines[index].strip()
                    if not nxt or starts_block(nxt, lines, index):
                        break
                    item += " " + nxt
                    index += 1
                entries.append((depth, tag, item))
            output.append(render_list(entries))
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines):
            next_line = lines[index].strip()
            if not next_line:
                break
            if (
                next_line.startswith(("#", ">", "```"))
                or next_line in {"---", "***", "___"}
                or BULLET_RE.match(next_line)
                or ORDERED_RE.match(next_line)
            ):
                break
            if "|" in next_line and index + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[index + 1].strip()):
                break
            paragraph.append(next_line)
            index += 1
        output.append(f"<p>{inline(' '.join(paragraph))}</p>")

    return "".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    markdown = args.source.read_text(encoding="utf-8")
    storage = convert(markdown)
    args.destination.write_text(storage, encoding="utf-8")
    print(f"wrote {args.destination} ({len(storage)} chars)")


if __name__ == "__main__":
    main()
