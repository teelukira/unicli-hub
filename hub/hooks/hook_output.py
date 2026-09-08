#!/usr/bin/env python3
"""hook_output.py — CLI-aware stdout helpers for the hook entry points.

Claude Code validates hook stdout against a strict schema. The top-level
`decision` field only accepts the legacy "approve"|"block", so the cross-CLI
`{"decision": "allow", "permission": "allow"}` payload fails validation and
surfaces as a `hook_non_blocking_error` on every single tool call. Claude's
allow/deny must travel through `hookSpecificOutput.permissionDecision`, and
"no objection" is expressed by printing nothing at all.

Cursor / Grok / Antigravity / Kiro still read the legacy `permission` shape,
so the output is branched on the event name carried in the payload.
"""

from __future__ import annotations

import json

# Claude Code sends PascalCase event names in `hook_event_name`.
# Cursor uses camelCase ("preToolUse", "beforeShellExecution", ...).
CLAUDE_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolBatch",
    "UserPromptSubmit",
    "PermissionRequest",
    "SessionStart",
    "SessionEnd",
    "Stop",
    "SubagentStop",
    "Notification",
    "PreCompact",
}


def claude_event(payload: object) -> str | None:
    """Return the Claude Code event name, or None when another CLI is calling."""
    if not isinstance(payload, dict):
        return None
    event = payload.get("hook_event_name")
    return event if isinstance(event, str) and event in CLAUDE_EVENTS else None


def allow_doc(payload: object) -> dict | None:
    """Output for 'no objection'. On Claude, silence means normal permission flow."""
    if not isinstance(payload, dict) or not payload:
        # Caller unknown (empty or unparseable stdin) — silence is valid everywhere.
        return None
    if claude_event(payload) is not None:
        return None
    return {"decision": "allow", "permission": "allow"}


def deny_doc(payload: object, reason: str) -> dict | None:
    """Output that refuses the tool call, in the calling CLI's schema."""
    event = claude_event(payload)
    if event is None:
        return {
            "decision": "deny",
            "reason": reason,
            "permission": "deny",
            "user_message": reason,
            "agent_message": reason,
        }
    if event != "PreToolUse":
        # Only PreToolUse can refuse; elsewhere stderr + exit code carry the reason.
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def emit(doc: dict | None) -> None:
    """Write a hook document to stdout. None means 'print nothing'."""
    if doc is not None:
        print(json.dumps(doc))
