#!/usr/bin/env python3
"""workflow_transition_guard.py — PreToolUse hook.

Blocks AI-DLC stage-completion edits in aidlc-state.md when required Jira or
gate markers are missing from audit.md. This keeps Cursor from marking
Code Generation / Build and Test complete before workflow prerequisites exist.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

STATE_FILE = "aidlc-docs/aidlc-state.md"
AUDIT_FILE = "aidlc-docs/audit.md"
WORKSTREAM_HEADER = re.compile(r"^## AI-DLC .*Workstream \(([^)]+)\)", re.MULTILINE)
CHECKED_CODEGEN = re.compile(r"^- \[x\] Code Generation\b", re.MULTILINE)
CHECKED_BUILD = re.compile(r"^- \[x\] Build and Test\b", re.MULTILINE)
REAL_JIRA_TICKET = re.compile(r"\*\*Jira Ticket\*\*:\s*NWAE-\d+")
PLACEHOLDER_JIRA_TICKET = re.compile(r"\*\*Jira Ticket\*\*:\s*TODO-NWAE-\d+")


def dig(payload: dict, *keys: str) -> str:
    node = payload
    for key in keys:
        if not isinstance(node, dict):
            return ""
        node = node.get(key, "")
    return node if isinstance(node, str) else ""


def extract_path(payload: dict) -> str:
    for keys in (
        ("tool_input", "file_path"),
        ("tool_input", "path"),
        ("toolInput", "file_path"),
        ("toolInput", "path"),
        ("args", "file_path"),
        ("args", "path"),
    ):
        value = dig(payload, *keys)
        if value:
            return value
    return ""


def extract_proposed_text(payload: dict, current_text: str) -> str:
    for keys in (
        ("tool_input", "content"),
        ("tool_input", "text"),
        ("tool_input", "body"),
        ("toolInput", "content"),
        ("toolInput", "text"),
        ("toolInput", "body"),
        ("args", "content"),
        ("args", "text"),
        ("args", "body"),
    ):
        value = dig(payload, *keys)
        if value:
            return value

    old_string = ""
    new_string = ""
    for keys in (
        ("tool_input", "old_string"),
        ("toolInput", "old_string"),
        ("args", "old_string"),
    ):
        old_string = dig(payload, *keys)
        if old_string:
            break

    for keys in (
        ("tool_input", "new_string"),
        ("toolInput", "new_string"),
        ("args", "new_string"),
    ):
        new_string = dig(payload, *keys)
        if new_string:
            break

    if old_string and new_string and old_string in current_text:
        return current_text.replace(old_string, new_string, 1)

    return ""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def normalize(path: str, root: Path) -> str:
    if not path:
        return ""
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    try:
        resolved = resolved.resolve()
    except FileNotFoundError:
        resolved = resolved.absolute()
    root = root.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return resolved.as_posix()


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
    match = WORKSTREAM_HEADER.search(first_line)
    if not match:
        return ""
    raw = match.group(1).strip()
    return raw.split()[0].strip(")").lower()


def has_marker(audit_text: str, marker: str) -> bool:
    return marker in audit_text


def has_regex(audit_text: str, pattern: str) -> bool:
    return re.search(pattern, audit_text, re.MULTILINE) is not None


def has_waiver(audit_text: str, waiver_name: str, unit: str) -> bool:
    return has_regex(
        audit_text,
        rf"{re.escape(waiver_name)}:\s*approved-by-user\s+\[unit={re.escape(unit)}\]\s+reason=",
    )


def find_codegen_plan(root: Path, unit: str) -> Path | None:
    unit_lower = unit.lower()
    candidates = sorted(
        path
        for path in root.rglob("code-generation-plan.md")
        if "aidlc-docs/" in path.as_posix()
    )
    preferred = [path for path in candidates if unit_lower in path.as_posix().lower()]
    if preferred:
        return preferred[0]
    return candidates[0] if candidates else None


def plan_has_open_checkboxes(path: Path | None) -> bool:
    if path is None or not path.is_file():
        return False
    try:
        return "- [ ]" in path.read_text(encoding="utf-8")
    except Exception:
        return False


def has_codegen_compliance(audit_text: str, unit: str) -> bool:
    return has_regex(
        audit_text,
        rf"## Codegen Principles Compliance .*?(?:\n.*){{0,8}}\n\*\*Unit\*\*:\s*{re.escape(unit.upper())}\b",
    )


def missing_codegen_requirements(
    root: Path, audit_text: str, unit: str, proposed_section: str
) -> list[str]:
    missing: list[str] = []
    if not has_marker(
        audit_text,
        f"APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]",
    ):
        missing.append("`APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit=...]`")

    if not has_waiver(audit_text, "JIRA-WAIVER", unit):
        if not (
            has_marker(audit_text, f"APPROVAL-JIRA-CREATE: granted [unit={unit}]")
            or has_regex(
                audit_text,
                rf"JIRA-REUSE:\s*\S+\s+\[unit={re.escape(unit)}\]",
            )
        ):
            missing.append("`APPROVAL-JIRA-CREATE: granted [unit=...]` or `JIRA-REUSE: <KEY> [unit=...]`")
        if not has_regex(audit_text, rf"JIRA-CREATED:\s*NWAE-\d+\s+\[unit={re.escape(unit)}\]"):
            missing.append("`JIRA-CREATED: NWAE-### [unit=...]`")

        if not has_regex(
            audit_text,
            rf"JIRA-INPROGRESS:\s*NWAE-\d+\s+\[unit={re.escape(unit)}\]",
        ):
            missing.append("`JIRA-INPROGRESS: NWAE-### [unit=...]`")
        if not REAL_JIRA_TICKET.search(proposed_section):
            missing.append("real `**Jira Ticket**: NWAE-###` in `aidlc-state.md`")
        if PLACEHOLDER_JIRA_TICKET.search(proposed_section):
            missing.append("placeholder Jira ticket must be reconciled or waived")

    if plan_has_open_checkboxes(find_codegen_plan(root, unit)):
        missing.append("all code-generation-plan.md checkboxes completed")

    if not has_codegen_compliance(audit_text, unit):
        missing.append("Codegen Principles Compliance audit entry for the active unit")

    return missing


def missing_build_requirements(audit_text: str, unit: str) -> list[str]:
    missing: list[str] = []
    if not has_marker(
        audit_text,
        f"APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]",
    ):
        missing.append("`APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit=...]`")

    if has_waiver(audit_text, "GATE-WAIVER", unit):
        return missing

    if not has_marker(audit_text, f"GATE-QA: PASS [unit={unit}]"):
        missing.append("`GATE-QA: PASS [unit=...]`")
    if not has_regex(audit_text, rf"GATE-TMF:\s*(PASS|N/A)\s+\[unit={re.escape(unit)}\]"):
        missing.append("`GATE-TMF: PASS|N/A [unit=...]`")
    if not has_regex(
        audit_text,
        rf"GATE-WEB:\s*(PASS|CONDITIONAL PASS|N/A)\s+\[unit={re.escape(unit)}\]",
    ):
        missing.append("`GATE-WEB: PASS|CONDITIONAL PASS|N/A [unit=...]`")

    # qa-tester subagent must be invoked (blocks self-waive by the main agent)
    qa_invoked = has_regex(
        audit_text,
        rf"SUBAGENT-INVOCATION:\s*qa-tester\s+\[unit={re.escape(unit)}\]",
    )
    qa_waiver = has_regex(
        audit_text,
        rf"GATE-WAIVER:\s*qa-tester\s+\[unit={re.escape(unit)}\]\s+reason=",
    )
    if not qa_invoked and not qa_waiver:
        missing.append(
            "qa-tester subagent invocation evidence "
            f"(`SUBAGENT-INVOCATION: qa-tester [unit={unit}]` in audit.md after Task invocation, "
            f"or `GATE-WAIVER: qa-tester [unit={unit}] reason=<...>` for wiring-only/non-code changes)"
        )
    return missing


def block(reason: str) -> int:
    payload = {
        "permission": "deny",
        "user_message": reason,
        "agent_message": reason,
        "hookSpecificOutput": {
            "hookType": "PreToolUse",
            "permissionDecision": "block",
            "permissionDecisionReason": reason,
        },
    }
    print(json.dumps(payload))
    return 1


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    root = repo_root()
    target = normalize(extract_path(payload), root)
    if target != STATE_FILE:
        return 0

    state_path = root / STATE_FILE
    audit_path = root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return 0

    current_text = state_path.read_text(encoding="utf-8")
    proposed_text = extract_proposed_text(payload, current_text)
    if not proposed_text:
        return 0

    branch = current_branch(root)
    if not branch:
        return 0

    current_section = section_for_branch(current_text, branch)
    proposed_section = section_for_branch(proposed_text, branch)
    if not current_section or not proposed_section:
        return 0

    unit = unit_from_section(proposed_section) or unit_from_section(current_section)
    if not unit:
        return 0

    audit_text = audit_path.read_text(encoding="utf-8")

    if CHECKED_CODEGEN.search(proposed_section) and not CHECKED_CODEGEN.search(current_section):
        missing = missing_codegen_requirements(root, audit_text, unit, proposed_section)
        if missing:
            return block(
                "AI-DLC workflow block: cannot mark Code Generation complete for "
                f"{unit.upper()} yet. Missing: {', '.join(missing)}"
            )

    if CHECKED_BUILD.search(proposed_section) and not CHECKED_BUILD.search(current_section):
        missing = missing_build_requirements(audit_text, unit)
        if missing:
            return block(
                "AI-DLC workflow block: cannot mark Build and Test complete for "
                f"{unit.upper()} yet. Missing: {', '.join(missing)}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
