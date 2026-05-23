#!/usr/bin/env python3
"""shell_sensitive_file_guard.py — beforeShellExecution hook.

Blocks shell-based mutations to AI-DLC state/audit/plan files so file-edit
hooks remain effective, and prevents push/merge when required workflow markers
are still missing for the active workstream.

For push/merge, resolves the Git checkout from the shell (``git -C <dir>`` before
the push/merge verb, a leading ``cd <dir> &&``, or payload cwd) so worktree
pushes are checked against that checkout's branch and ``aidlc-docs/``, not the
Cursor workspace root's current branch alone.
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
PUSH_OR_MERGE = re.compile(
    r"\bgit\s+push\b|\bgit\s+merge\b(?=\s|$)|\bgh\s+pr\s+create\b"
)
GIT_DASH_C = re.compile(r"\bgit\s+-C\s+(\"([^\"]+)\"|'([^']+)'|(\S+))")


def git_rev_parse_toplevel(path: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        line = result.stdout.strip()
        if line:
            return Path(line).resolve()
    except (OSError, subprocess.CalledProcessError):
        pass
    return None


def parse_last_git_dash_c_before_push(command: str) -> Path | None:
    for name in ("push", "merge"):
        m_push = re.search(rf"\bgit\s+{re.escape(name)}\b", command)
        if m_push:
            prefix = command[: m_push.start()]
            matches = list(GIT_DASH_C.finditer(prefix))
            if matches:
                m = matches[-1]
                raw = m.group(2) or m.group(3) or m.group(4)
                return Path(raw).expanduser()
            return None
    if re.search(r"\bgh\s+pr\s+create\b", command):
        matches = list(GIT_DASH_C.finditer(command))
        if matches:
            m = matches[-1]
            raw = m.group(2) or m.group(3) or m.group(4)
            return Path(raw).expanduser()
    return None


def parse_leading_cd(command: str) -> Path | None:
    s = command.strip()
    m = re.match(r"cd\s+(\"([^\"]+)\"|'([^']+)'|(\S+))\s+&&\s+", s)
    if not m:
        return None
    raw = m.group(2) or m.group(3) or m.group(4)
    return Path(raw).expanduser()


def cwd_from_payload(payload: dict) -> Path | None:
    for keys in (
        ("cwd",),
        ("working_directory",),
        ("workingDirectory",),
        ("tool_input", "cwd"),
        ("toolInput", "cwd"),
        ("tool_input", "working_directory"),
        ("toolInput", "workingDirectory"),
    ):
        value = dig(payload, *keys)
        if value:
            return Path(value).expanduser()
    return None


def resolve_push_git_root(command: str, payload: dict) -> Path | None:
    for candidate in (
        parse_last_git_dash_c_before_push(command),
        parse_leading_cd(command),
        cwd_from_payload(payload),
    ):
        if candidate is None:
            continue
        top = git_rev_parse_toplevel(candidate)
        if top is not None:
            return top
    return git_rev_parse_toplevel(repo_root())


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
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        )
        branch = result.stdout.strip()
        if branch and branch != "HEAD":
            return branch
    except Exception:
        pass
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

    command = extract_command(payload)
    if not command:
        return allow()

    if is_sensitive_shell_mutation(command):
        return block(
            "AI-DLC shell block: do not mutate `aidlc-state.md`, `audit.md`, or plan files via shell. "
            "Use file edit tools so workflow hooks can validate the change."
        )

    if not PUSH_OR_MERGE.search(command):
        return allow()

    push_root = resolve_push_git_root(command, payload)
    if push_root is None:
        return allow()

    state_path = push_root / STATE_FILE
    audit_path = push_root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return allow()

    branch = current_branch(push_root)
    section = section_for_branch(state_path.read_text(encoding="utf-8"), branch)
    if not section:
        return allow()

    unit = unit_from_section(section)
    if not unit:
        return allow()

    missing = check_missing_workflow_markers(
        section,
        audit_path.read_text(encoding="utf-8"),
        unit,
    )
    if not missing:
        return allow()

    return block(
        "AI-DLC workflow block: push/merge is not allowed while the active workstream still "
        f"has unresolved workflow markers for {unit.upper()}: {', '.join(missing)}"
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": (
                        "shell_sensitive_file_guard.py crashed; refusing shell command until fixed. "
                        + traceback.format_exc(limit=3)
                    ),
                    "agent_message": "shell_sensitive_file_guard.py exception — see hook user_message",
                }
            )
        )
        raise SystemExit(1)
