# hub/hooks — Reference Hook Stubs

This directory contains **minimal reference stubs** for the unicli-hub hook system.
Each stub demonstrates the stdin/stdout contract for one event category.
Copy and extend them with your own gate or sync logic.

## Event Vocabulary by CLI

| Category | Claude Code | Cursor | Gemini CLI | Antigravity |
|----------|-------------|--------|------------|-------------|
| Before tool | `PreToolUse` | `preToolUse` | `BeforeTool` | — |
| After tool | `PostToolUse` | `postToolUse` | `AfterTool` | — |
| Before shell | `PreToolUse` (matcher: `Bash`) | `beforeShellExecution` | `BeforeTool` | — |
| Before MCP | `PreToolUse` (matcher: `mcp__*`) | `beforeMCPExecution` | `BeforeTool` | — |
| Session start | `SessionStart` | — | — | — |
| Stop | `Stop` | `stop` | — | — |
| After response | — | `afterAgentResponse` | — | — |

## SSOT Hook Config Files

| File | Consumed by |
|------|-------------|
| `hub/claude-hooks.json` | → `.claude/settings.json` (fanout) |
| `hub/cursor-hooks.json` | → `.cursor/hooks.json` (fanout) |
| `hub/gemini-hooks.json` | → `.gemini/settings.json` hooks block (fanout) |

Hooks are fanned out by `.unicli-hub/scripts/render_hooks.py` via `./sync.sh --fix`.

## Stub Files

| File | Category |
|------|----------|
| `pre_tool_use.py` | Gate — runs before any tool |
| `post_tool_use.py` | Audit/sync — runs after any tool |
| `before_shell_execution.py` | Gate — runs before shell commands |
| `before_mcp_execution.py` | Gate — runs before MCP tool calls |
| `session_start.py` | Context injection at session start |
| `stop.py` | Notification/cleanup at agent stop |

## Stdin/Stdout Contract

All hooks read JSON from stdin and write JSON to stdout (for gate hooks):

```json
// Gate hook response
{"permission": "allow"}
// or
{"permission": "deny", "reason": "Human-readable explanation"}
```

Exit code 0 = allow (fallback when stdout is empty or non-JSON).
