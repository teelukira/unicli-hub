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


_GATED_TOOL = "gitlab_create_merge_request"
_GATED_TOOL_BARE = "create_merge_request"

_TEMPLATE_SECTIONS = ("## 지라 (Jira)", "## AI-DLC")


def extract_mr_description(payload: dict) -> str:
    for key in ("tool_input", "input", "args"):
        node = payload.get(key)
        if isinstance(node, dict):
            desc = node.get("description", "") or ""
            if desc:
                return desc
            arguments = node.get("Arguments") or node.get("arguments")
            if isinstance(arguments, dict):
                desc = arguments.get("description", "") or ""
                if desc:
                    return desc
    return ""


def validate_mr_description(description: str, expected_ticket: str) -> tuple[bool, str]:
    if not description.strip():
        return False, (
            "MR 설명이 비어 있습니다. "
            "`.gitlab/merge_request_templates/default.md` 템플릿을 사용하세요."
        )
    for section in _TEMPLATE_SECTIONS:
        if section not in description:
            return False, (
                f"MR 설명에 `{section}` 섹션이 없습니다. "
                "한국어 팀 템플릿(`.gitlab/merge_request_templates/default.md`)을 사용하세요."
            )
    jira_match = re.search(
        r"## 지라 \(Jira\)(.*?)(?=^##|\Z)", description, re.DOTALL | re.MULTILINE
    )
    if jira_match:
        jira_text = re.sub(r"<!--.*?-->", "", jira_match.group(1), flags=re.DOTALL)
        if not re.search(r"NWAE-\d+", jira_text):
            hint = f" (state.md 기준 예상 티켓: {expected_ticket})" if expected_ticket else ""
            return False, (
                f"MR 지라 섹션에 실제 티켓 번호(NWAE-XXX)가 없습니다{hint}. "
                "템플릿 주석을 실제 티켓 번호로 교체하세요."
            )
    return True, ""


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


def allow() -> int:
    print(json.dumps({"permission": "allow"}))
    return 0


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return allow()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return allow()

    tool_name = extract_tool_name(payload)
    if tool_name != _GATED_TOOL:
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

    description = extract_mr_description(payload)
    ticket = jira_ticket_from_section(section)
    ok, reason = validate_mr_description(description, ticket)
    if not ok:
        return block(f"AI-DLC GitLab MR block: {reason}")

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
                        "gitlab_mr_gate_guard.py crashed; refusing GitLab MR MCP until fixed. "
                        + traceback.format_exc(limit=5)
                    ),
                    "agent_message": "gitlab_mr_gate_guard.py exception — see hook user_message",
                }
            )
        )
        raise SystemExit(1)
