#!/usr/bin/env python3
"""jira_gate_guard.py — beforeMCPExecution hook.

Blocks Jira MCP mutations when the required approval or reconciliation markers
are missing for the active AI-DLC workstream.
"""

from __future__ import annotations

import json
import re
import select
import subprocess
import sys
import traceback
from pathlib import Path

STATE_FILE = "aidlc-docs/aidlc-state.md"
AUDIT_FILE = "aidlc-docs/audit.md"


def dig(payload: dict, *keys: str) -> str:
    node = payload
    for key in keys:
        if not isinstance(node, dict):
            return ""
        node = node.get(key, "")
    return node if isinstance(node, str) else ""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def current_branch(root: Path) -> str:
    commands = (
        ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
        ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"],
        ["git", "-C", str(root), "branch", "--show-current"],
    )
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            branch = result.stdout.strip()
            if branch and branch != "HEAD":
                return branch
        except Exception:
            continue
    return ""


def split_workstream_sections(text: str) -> list[str]:
    matches = list(re.finditer(r"^## AI-DLC .*Workstream \([^)]+\)", text, re.MULTILINE))
    sections: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(text[start:end])
    return sections


def section_for_branch(text: str, branch: str) -> str:
    if not branch:
        return ""
    for section in split_workstream_sections(text):
        if f"- **Branch**: `{branch}`" in section or f"- **Branch**: {branch}" in section:
            return section
    return ""


def unit_from_section(section: str) -> str:
    if not section:
        return ""
    first_line = section.splitlines()[0] if section.splitlines() else ""
    match = re.search(r"\(([^ )]+)", first_line)
    return match.group(1).lower() if match else ""


def jira_ticket_from_section(section: str) -> str:
    match = re.search(r"\*\*Jira Ticket\*\*:\s*(NWAE-\d+)", section)
    return match.group(1) if match else ""


_GATED_BARE: tuple[str, ...] = (
    "jira_create_issue",
    "jira_transition_issue",
    "jira_update_issue",
)


def extract_tool_name(payload: dict) -> str:
    for keys in (
        ("tool_name",),
        ("toolName",),
        ("mcp_tool_name",),
        ("mcpToolName",),
        ("tool", "name"),
        ("mcp", "toolName"),
        ("args", "tool_name"),
        ("args", "toolName"),
        ("args", "ToolName"),
        ("tool_input", "ToolName"),
        ("arguments", "ToolName"),
        ("args", "Arguments", "ToolName"),
        ("tool_input", "Arguments", "ToolName"),
    ):
        value = dig(payload, *keys)
        if value:
            # Normalize MCP prefixes (Claude: mcp__ns__tool, Gemini: mcp_server_tool) → bare tool name
            for bare in _GATED_BARE:
                if value == bare or value.endswith(f"__{bare}") or value.endswith(f"_{bare}"):
                    return bare
            return value

    raw = json.dumps(payload, ensure_ascii=False)
    for candidate in _GATED_BARE:
        if candidate in raw:
            return candidate
    return ""


def has_marker(audit_text: str, marker: str) -> bool:
    return marker in audit_text


def has_regex(audit_text: str, pattern: str) -> bool:
    return re.search(pattern, audit_text, re.MULTILINE) is not None


def has_waiver(audit_text: str, unit: str) -> bool:
    return has_regex(
        audit_text,
        rf"JIRA-WAIVER:\s*approved-by-user\s+\[unit={re.escape(unit)}\]\s+reason=",
    )


def block(reason: str) -> int:
    print(reason, file=sys.stderr)
    print(json.dumps({
        "permission": "deny",
        "user_message": reason,
        "agent_message": reason,
        "hookSpecificOutput": {
            "hookType": "PreToolUse",
            "permissionDecision": "block",
            "permissionDecisionReason": reason,
        },
    }))
    return 1


def allow() -> int:
    print(json.dumps({"permission": "allow"}))
    return 0


def _read_stdin(timeout: float = 5.0) -> str:
    if sys.stdin.isatty():
        return ""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        return sys.stdin.read() if ready else ""
    except Exception:
        return ""


def main() -> int:
    raw = _read_stdin()
    if not raw.strip():
        return allow()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return allow()

    tool_name = extract_tool_name(payload)
    if tool_name not in _GATED_BARE:
        return allow()

    root = repo_root()
    state_path = root / STATE_FILE
    audit_path = root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return allow()

    branch = current_branch(root)
    state_text = state_path.read_text(encoding="utf-8")
    section = section_for_branch(state_text, branch)
    if not section:
        return allow()

    unit = unit_from_section(section)
    if not unit:
        return allow()

    audit_text = audit_path.read_text(encoding="utf-8")
    if has_waiver(audit_text, unit):
        return allow()

    if tool_name == "jira_create_issue":
        if not has_marker(audit_text, f"APPROVAL-JIRA-CREATE: granted [unit={unit}]"):
            return block(
                "AI-DLC Jira block: explicit Jira creation approval marker is missing. "
                f"Record `APPROVAL-JIRA-CREATE: granted [unit={unit}]` in `aidlc-docs/audit.md` first."
            )
        return allow()

    jira_ticket = jira_ticket_from_section(section)
    if not jira_ticket:
        return block(
            "AI-DLC Jira block: active workstream has no real `**Jira Ticket**: NWAE-###` "
            "recorded in `aidlc-state.md`."
        )

    if not has_regex(audit_text, rf"JIRA-CREATED:\s*{re.escape(jira_ticket)}\s+\[unit={re.escape(unit)}\]"):
        return block(
            "AI-DLC Jira block: ticket exists in state but the create marker is missing. "
            f"Record `JIRA-CREATED: {jira_ticket} [unit={unit}]` in `aidlc-docs/audit.md` first."
        )

    return allow()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": (
                        "jira_gate_guard.py crashed; refusing Jira MCP until fixed. "
                        + traceback.format_exc(limit=5)
                    ),
                    "agent_message": "jira_gate_guard.py exception — see hook user_message",
                }
            )
        )
        raise SystemExit(1)
