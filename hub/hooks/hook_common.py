"""hook_common.py — shared AI-DLC hook logic."""

from __future__ import annotations

import importlib.util
import json
import re
import select
import subprocess
import sys
from pathlib import Path

STATE_FILE = "aidlc-docs/aidlc-state.md"
AUDIT_FILE = "aidlc-docs/audit.md"
RULES_ROOT_NAME = "hub"
GATED_JIRA = ("jira_create_issue", "jira_transition_issue", "jira_update_issue")
GITLAB_TOOL = "gitlab_create_merge_request"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _load_module(name: str):
    path = Path(__file__).parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"aidlc_hook_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def read_stdin_payload(timeout: float = 5.0) -> str:
    """Read stdin without blocking indefinitely.

    Returns empty string immediately when stdin is a terminal.
    Otherwise waits at most `timeout` seconds via select() before giving up.
    """
    if sys.stdin.isatty():
        return ""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return ""
        return sys.stdin.read()
    except Exception:
        return ""


def allow() -> int:
    print(json.dumps({"permission": "allow"}))
    return 0


def block(reason: str, *, hook_type: str = "PreToolUse") -> int:
    print(reason, file=sys.stderr)
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": reason,
                "agent_message": reason,
                "hookSpecificOutput": {
                    "hookType": hook_type,
                    "permissionDecision": "block",
                    "permissionDecisionReason": reason,
                },
            }
        )
    )
    return 1


def resolve_tool_name(argv_hint: str, payload: dict) -> str:
    jg = _load_module("jira_gate_guard")
    bare = jg.extract_tool_name(payload)
    if bare:
        return bare
    if argv_hint:
        for name in (*GATED_JIRA, GITLAB_TOOL, "create_merge_request"):
            if argv_hint == name or name in argv_hint:
                return GITLAB_TOOL if "gitlab" in argv_hint and "merge" in argv_hint else name
    raw = json.dumps(payload, ensure_ascii=False)
    for name in GATED_JIRA:
        if name in raw:
            return name
    if GITLAB_TOOL in raw or "create_merge_request" in raw:
        return GITLAB_TOOL
    return argv_hint


def check_jira_gate(payload: dict, argv_hint: str = "") -> str | None:
    jg = _load_module("jira_gate_guard")
    tool = resolve_tool_name(argv_hint, payload)
    if tool not in GATED_JIRA:
        return None
    root = repo_root()
    audit_path = root / AUDIT_FILE
    state_path = root / STATE_FILE
    if not audit_path.is_file() or not state_path.is_file():
        return None
    branch = jg.current_branch(root)
    section = jg.section_for_branch(state_path.read_text(encoding="utf-8"), branch)
    if not section:
        return None
    unit = jg.unit_from_section(section)
    if not unit:
        return None
    audit_text = audit_path.read_text(encoding="utf-8")
    if jg.has_waiver(audit_text, unit):
        return None
    if tool == "jira_create_issue":
        if not jg.has_marker(audit_text, f"APPROVAL-JIRA-CREATE: granted [unit={unit}]"):
            return (
                "AI-DLC Jira block: explicit Jira creation approval marker is missing. "
                f"Record `APPROVAL-JIRA-CREATE: granted [unit={unit}]` in `aidlc-docs/audit.md` first."
            )
        return None
    ticket = jg.jira_ticket_from_section(section)
    if not ticket:
        return (
            "AI-DLC Jira block: active workstream has no real `**Jira Ticket**: NWAE-###` "
            "recorded in `aidlc-docs/aidlc-state.md`."
        )
    if not jg.has_regex(audit_text, rf"JIRA-CREATED:\s*{re.escape(ticket)}\s+\[unit={re.escape(unit)}\]"):
        return (
            "AI-DLC Jira block: ticket exists in state but the create marker is missing. "
            f"Record `JIRA-CREATED: {ticket} [unit={unit}]` in `aidlc-docs/audit.md` first."
        )
    return None


def check_gitlab_gate(payload: dict, argv_hint: str = "") -> str | None:
    gg = _load_module("gitlab_mr_gate_guard")
    tool = resolve_tool_name(argv_hint, payload)
    if tool != GITLAB_TOOL:
        return None
    root = repo_root()
    audit_path = root / AUDIT_FILE
    state_path = root / STATE_FILE
    if not audit_path.is_file() or not state_path.is_file():
        return None
    branch = gg.current_branch(root)
    section = gg.section_for_branch(state_path.read_text(encoding="utf-8"), branch)
    if not section:
        return None
    unit = gg.unit_from_section(section)
    if not unit:
        return None
    audit_text = audit_path.read_text(encoding="utf-8")
    if gg.has_waiver(audit_text, unit):
        return None
    if not gg.has_regex(audit_text, rf"APPROVAL-MR-CREATE:\s*granted\s+\[unit={re.escape(unit)}\]"):
        return (
            "AI-DLC GitLab MR block: MR creation approval marker is missing. "
            f"Record `APPROVAL-MR-CREATE: granted [unit={unit}]` in `{AUDIT_FILE}` first."
        )
    if not gg.has_regex(
        audit_text,
        rf"APPROVAL-STAGE:\s*BUILD_AND_TEST_APPROVED\s+\[unit={re.escape(unit)}\]",
    ):
        return (
            "AI-DLC GitLab MR block: Build and Test stage approval is missing. "
            f"Record `APPROVAL-STAGE: BUILD_AND_TEST_APPROVED [unit={unit}]` in `{AUDIT_FILE}` first."
        )
    if not gg.jira_ticket_from_section(section):
        return (
            "AI-DLC GitLab MR block: active workstream has no real `**Jira Ticket**: NWAE-###` "
            f"in `{STATE_FILE}`, and no `JIRA-WAIVER` for this unit."
        )
    return None


def check_workflow_transition(payload: dict) -> str | None:
    wf = _load_module("workflow_transition_guard")
    path = wf.extract_path(payload)
    _norm = wf.normalize_path if hasattr(wf, "normalize_path") else wf.normalize
    rel = _norm(path, wf.repo_root())
    if rel != STATE_FILE:
        return None
    root = wf.repo_root()
    state_path = root / STATE_FILE
    audit_path = root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return None
    current_text = state_path.read_text(encoding="utf-8")
    proposed_text = wf.extract_proposed_text(payload, current_text)
    if not proposed_text:
        return None
    branch = wf.current_branch(root)
    if not branch:
        return None
    current_section = wf.section_for_branch(current_text, branch)
    proposed_section = wf.section_for_branch(proposed_text, branch)
    if not current_section or not proposed_section:
        return None
    unit = wf.unit_from_section(proposed_section) or wf.unit_from_section(current_section)
    if not unit:
        return None
    audit_text = audit_path.read_text(encoding="utf-8")
    if wf.CHECKED_CODEGEN.search(proposed_section) and not wf.CHECKED_CODEGEN.search(current_section):
        missing = wf.missing_codegen_requirements(root, audit_text, unit, proposed_section)
        if missing:
            return (
                "AI-DLC workflow block: cannot mark Code Generation complete for "
                f"{unit.upper()} yet. Missing: {', '.join(missing)}"
            )
    if wf.CHECKED_BUILD.search(proposed_section) and not wf.CHECKED_BUILD.search(current_section):
        missing = wf.missing_build_requirements(audit_text, unit)
        if missing:
            return (
                "AI-DLC workflow block: cannot mark Build and Test complete for "
                f"{unit.upper()} yet. Missing: {', '.join(missing)}"
            )
    return None


def check_code_location(path: str) -> str | None:
    cl = _load_module("code_location_guard")
    if hasattr(cl, "guard_code_location"):
        return cl.guard_code_location(path)
    normalized = path.replace("\\", "/")
    if "aidlc-docs/" in normalized and cl.is_code_file(path):
        return (
            f"AI-DLC rule: `aidlc-docs/`에는 문서(.md)만 둘 수 있습니다. "
            f"코드/설정 파일은 워크스페이스 루트로 이동하세요: {path}"
        )
    return None


def check_generated_file(path: str) -> str | None:
    from fnmatch import fnmatch as _fnmatch
    gf = _load_module("generated_file_guard")
    if hasattr(gf, "guard_generated_files"):
        return gf.guard_generated_files(path)
    normalize = gf.normalize if hasattr(gf, "normalize") else (lambda p: p)
    rel = normalize(path)
    for guard_path, hint in gf.EXACT_GUARDS:
        if rel == guard_path:
            return (
                f"Generated file block: direct edit of `{rel}` is not allowed. "
                f"Edit the canonical source instead: {hint}. "
                "Then run `./sync.sh --fix`."
            )
    for pattern, hint_tmpl in gf.GLOB_GUARDS:
        if _fnmatch(rel, pattern):
            hint = gf.resolve_hint(pattern, rel, hint_tmpl) if hasattr(gf, "resolve_hint") else hint_tmpl
            return (
                f"Generated file block: direct edit of `{rel}` is not allowed. "
                f"Edit the canonical source instead: {hint}. "
                "Then run `./sync.sh --fix`."
            )
    return None


def check_shell_guard(payload: dict) -> str | None:
    sh = _load_module("shell_sensitive_file_guard")
    command = sh.extract_command(payload)
    if not command:
        return None
    if sh.is_sensitive_shell_mutation(command):
        return (
            "AI-DLC shell block: do not mutate `aidlc-state.md`, `audit.md`, or plan files via shell. "
            "Use file edit tools so workflow hooks can validate the change."
        )
    if not sh.PUSH_OR_MERGE.search(command):
        return None
    push_root = sh.resolve_push_git_root(command, payload)
    if push_root is None:
        return None
    state_path = push_root / STATE_FILE
    audit_path = push_root / AUDIT_FILE
    if not state_path.is_file() or not audit_path.is_file():
        return None
    branch = sh.current_branch(push_root)
    section = sh.section_for_branch(state_path.read_text(encoding="utf-8"), branch)
    if not section:
        return None
    unit = sh.unit_from_section(section)
    if not unit:
        return None
    missing = sh.check_missing_workflow_markers(
        section, audit_path.read_text(encoding="utf-8"), unit
    )
    if not missing:
        return None
    return (
        "AI-DLC workflow block: push/merge is not allowed while the active workstream still "
        f"has unresolved workflow markers for {unit.upper()}: {', '.join(missing)}"
    )


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
        ("args", "TargetFile"),
        ("tool_input", "TargetFile"),
        ("file_path",),
        ("path",),
        ("TargetFile",),
    ):
        val = dig(payload, *keys)
        if val:
            return val
    return ""


def extract_command(payload: dict) -> str:
    for keys in (
        ("command",),
        ("shell_command",),
        ("shellCommand",),
        ("args", "command"),
        ("tool_input", "command"),
        ("toolInput", "command"),
        ("args", "CommandLine"),
        ("tool_input", "CommandLine"),
        ("CommandLine",),
    ):
        val = dig(payload, *keys)
        if val:
            return val
    return ""


def normalize_path(path: str, root: Path | None = None) -> str:
    root = root or repo_root()
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    try:
        return resolved.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.replace("\\", "/").lstrip("/")


SKILL_SYNC_PREFIXES = (
    "hub/skills/",
    ".cursor/skills/",
    ".claude/skills/",
    ".antigravitycli/skills/",
)


def is_skill_sync_path(path: str) -> bool:
    if not path:
        return False
    normalized = path.replace("\\", "/")
    if not normalized.endswith("SKILL.md"):
        return False
    return any(prefix in normalized for prefix in SKILL_SYNC_PREFIXES)


def is_edit_tool(tool: str) -> bool:
    return tool.lower() in {
        "write_file", "replace", "edit", "write", "multiedit", "multi_edit",
        "strreplace", "apply_patch", "write_to_file", "replace_file_content",
        "multi_replace_file_content",
    }


def is_read_tool(tool: str) -> bool:
    return tool.lower() in {"read_file", "read", "readfile", "view_file"}


def is_shell_tool(tool: str) -> bool:
    return tool.lower() in {"run_shell_command", "bash", "shell", "beforeshellexecution", "run_command"}


def run_sync(root: Path | None = None) -> None:
    root = root or repo_root()
    lock_sync = root / RULES_ROOT_NAME / "hooks" / "lock_sync.py"
    try:
        subprocess.run([sys.executable, str(lock_sync)], cwd=str(root), check=False, timeout=60, stdout=sys.stderr)
    except subprocess.TimeoutExpired:
        print("hook_common: run_sync timed out after 60s", file=sys.stderr)



def adr_memory_nudge(path: str) -> str | None:
    ad = _load_module("adr_memory_sync_nudge")
    if hasattr(ad, "nudge_for_path"):
        return ad.nudge_for_path(path)
    return None


def check_adr_backlink(path: str) -> str | None:
    ab = _load_module("adr_backlink_check")
    if hasattr(ab, "check_path"):
        return ab.check_path(path)
    return None

