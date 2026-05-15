#!/usr/bin/env python3
"""shell_sensitive_file_guard.py — beforeShellExecution hook.

Blocks shell-based mutations to AI-DLC state/audit/plan files so file-edit
hooks remain effective, and prevents push/merge when required workflow markers
are still missing for the active workstream.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

STATE_FILE = "aidlc-docs/aidlc-state.md"
AUDIT_FILE = "aidlc-docs/audit.md"
CHECKED_CODEGEN = re.compile(r"^- \[x\] Code Generation\b", re.MULTILINE)
CHECKED_BUILD = re.compile(r"^- \[x\] Build and Test\b", re.MULTILINE)
REAL_JIRA_TICKET = re.compile(r"\*\*Jira Ticket\*\*:\s*NWAE-\d+")
SENSITIVE_PATH_HINTS = (
    STATE_FILE,
    AUDIT_FILE,
    "code-generation-plan.md",
    "build-and-test-summary.md",
)
MUTATING_PATTERNS = (
    re.compile(r"\bsed\b.*\s-i\b"),
    re.compile(r"\bperl\b.*\s-i\b"),
    re.compile(r"\btee\b"),
    re.compile(r">>"),
    re.compile(r"(?<!2)>"),
    re.compile(r"\bpython(?:3)?\b.*\b(open|Path)\b", re.IGNORECASE),
)
PUSH_OR_MERGE = re.compile(r"\bgit\s+(push|merge)\b|\bgh\s+pr\s+create\b")


def dig(payload: dict, *keys: str) -> str:
    node = payload
    for key in keys:
        if not isinstance(node, dict):
            return ""
        node = node.get(key, "")
    return node if isinstance(node, str) else ""


def extract_command(payload: dict) -> str:
    for keys in (
        ("command",),
        ("shell_command",),
        ("shellCommand",),
        ("args", "command"),
        ("tool_input", "command"),
        ("toolInput", "command"),
    ):
        value = dig(payload, *keys)
        if value:
            return value
    return ""


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


def has_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.MULTILINE) is not None


def has_waiver(audit_text: str, waiver_name: str, unit: str) -> bool:
    return has_regex(
        audit_text,
        rf"{re.escape(waiver_name)}:\s*approved-by-user\s+\[unit={re.escape(unit)}\]\s+reason=",
    )


def check_missing_workflow_markers(section: str, audit_text: str, unit: str) -> list[str]:
    missing: list[str] = []

    if CHECKED_CODEGEN.search(section) and not has_waiver(audit_text, "JIRA-WAIVER", unit):
        if f"APPROVAL-STAGE: CODE_GENERATION_APPROVED [unit={unit}]" not in audit_text:
            missing.append("code generation approval marker")
        if f"APPROVAL-JIRA-CREATE: granted [unit={unit}]" not in audit_text:
            missing.append("Jira create approval marker")
        if not has_regex(audit_text, rf"JIRA-CREATED:\s*NWAE-\d+\s+\[unit={re.escape(unit)}\]"):
            missing.append("JIRA-CREATED marker")
        if not has_regex(audit_text, rf"JIRA-INPROGRESS:\s*NWAE-\d+\s+\[unit={re.escape(unit)}\]"):
            missing.append("JIRA-INPROGRESS marker")
        if not REAL_JIRA_TICKET.search(section):
            missing.append("real Jira ticket in aidlc-state.md")

    if CHECKED_BUILD.search(section) and not has_waiver(audit_text, "GATE-WAIVER", unit):
        if f"APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]" not in audit_text:
            missing.append("build-and-test approval marker")
        if f"GATE-QA: PASS [unit={unit}]" not in audit_text:
            missing.append("QA PASS marker")
        if not has_regex(audit_text, rf"GATE-TMF:\s*(PASS|N/A)\s+\[unit={re.escape(unit)}\]"):
            missing.append("TMF PASS/N/A marker")
        if not has_regex(
            audit_text,
            rf"GATE-WEB:\s*(PASS|CONDITIONAL PASS|N/A)\s+\[unit={re.escape(unit)}\]",
        ):
            missing.append("Web PASS/CONDITIONAL PASS/N/A marker")

    return missing


def is_sensitive_shell_mutation(command: str) -> bool:
    if not any(path_hint in command for path_hint in SENSITIVE_PATH_HINTS):
        return False
    return any(pattern.search(command) for pattern in MUTATING_PATTERNS)


def block(reason: str) -> int:
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": reason,
                "agent_message": reason,
            }
        )
    )
    return 1


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    command = extract_command(payload)
    if not command:
        return 0

    if is_sensitive_shell_mutation(command):
        return block(
            "AI-DLC shell block: do not mutate `aidlc-state.md`, `audit.md`, or plan files via shell. "
            "Use file edit tools so workflow hooks can validate the change."
        )

    if not PUSH_OR_MERGE.search(command):
        return 0

    root = repo_root()
    state_path = root / STATE_FILE
    audit_path = root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return 0

    branch = current_branch(root)
    section = section_for_branch(state_path.read_text(encoding="utf-8"), branch)
    if not section:
        return 0

    unit = unit_from_section(section)
    if not unit:
        return 0

    missing = check_missing_workflow_markers(
        section,
        audit_path.read_text(encoding="utf-8"),
        unit,
    )
    if not missing:
        return 0

    return block(
        "AI-DLC workflow block: push/merge is not allowed while the active workstream still "
        f"has unresolved workflow markers for {unit.upper()}: {', '.join(missing)}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
