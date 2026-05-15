#!/usr/bin/env python3
"""gitlab_mr_gate_guard.py — beforeMCPExecution hook.

Blocks GitLab MR creation when audit/state markers for the active AI-DLC
workstream are missing (pairs with templates/cursor-workflow-slim.md).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
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


_GATED_TOOL = "gitlab_create_merge_request"
_GATED_TOOL_BARE = "create_merge_request"


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
    ):
        value = dig(payload, *keys)
        if value:
            # Normalize MCP prefixes (Claude: mcp__ns__tool, Gemini: mcp_server_tool) → bare tool name
            if value == _GATED_TOOL or value.endswith(f"__{_GATED_TOOL_BARE}") or value.endswith(f"_{_GATED_TOOL_BARE}"):
                return _GATED_TOOL
            return value

    raw = json.dumps(payload, ensure_ascii=False)
    if _GATED_TOOL in raw or _GATED_TOOL_BARE in raw:
        return _GATED_TOOL
    return ""


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


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_name = extract_tool_name(payload)
    if tool_name != _GATED_TOOL:
        return 0

    root = repo_root()
    state_path = root / STATE_FILE
    audit_path = root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return 0

    branch = current_branch(root)
    state_text = state_path.read_text(encoding="utf-8")
    section = section_for_branch(state_text, branch)
    if not section:
        return 0

    unit = unit_from_section(section)
    if not unit:
        return 0

    audit_text = audit_path.read_text(encoding="utf-8")

    if not has_regex(
        audit_text,
        rf"APPROVAL-MR-CREATE:\s*granted\s+\[unit={re.escape(unit)}\]",
    ):
        return block(
            "AI-DLC GitLab MR block: MR creation approval marker is missing. "
            f"Record `APPROVAL-MR-CREATE: granted [unit={unit}]` in `{AUDIT_FILE}` first."
        )

    if not has_regex(
        audit_text,
        rf"APPROVAL-STAGE:\s*BUILD_AND_TEST_APPROVED\s+\[unit={re.escape(unit)}\]",
    ):
        return block(
            "AI-DLC GitLab MR block: Build and Test stage approval is missing. "
            f"Record `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` in `{AUDIT_FILE}` first."
        )

    if not has_waiver(audit_text, unit):
        if not jira_ticket_from_section(section):
            return block(
                "AI-DLC GitLab MR block: active workstream has no real `**Jira Ticket**: NWAE-###` "
                f"in `{STATE_FILE}`, and no `JIRA-WAIVER` for this unit."
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
