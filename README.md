# UniCLI-Hub: The Frugal AI Nomad's Workspace

> *(Company won't sponsor your tools? We got you.)*

**UniCLI-Hub** is a centralized **SSOT (Single Source of Truth) Framework** for developers who are tired of AI subscription fatigue and context fragmentation.

## The Problem: Subscription Fatigue & Context Fragmentation

AI tools are amazing, but paying $20/month for *every single one* is unsustainable. When you jump between free tiers of different AI CLIs (Claude, Gemini, Cursor, etc.) to bypass rate limits, your AI's "brain" becomes fragmented. You lose your custom skills, agents, and project memory.

## The Solution: One Hub to Rule Them All

**UniCLI-Hub** centralizes your **Agents, Skills, Hooks, and MCP Servers** in a single directory. It automatically fans out these assets to all supported CLI tools, ensuring that no matter which tool you are using *right now*, it has the same context and capabilities.

**With UniCLI-Hub, you can:**
- **Switch Seamlessly:** Run out of Claude tokens? Switch to Antigravity (agy) without re-explaining your architecture.
- **Unified Memory:** Share project facts, conventions, and glossaries across all tools.
- **Automated Tooling:** Centralize MCP server definitions and hook logic.
- **Save Money:** Maximize the value of free tiers by treating multiple tools as a single "Pro" experience.

> Prefer 한국어? See [README.ko.md](./README.ko.md).

---

## Supported CLIs

| CLI | Derived location | Entry point |
|-----|------------------|-------------|
| **Antigravity (agy)** | `.agents/` | `AGENTS.md` |
| **Claude Code** | `.claude/` | `CLAUDE.md` |
| **Cursor** | `.cursor/` | `.cursor/rules/*.mdc` |
| **Kiro** | `.kiro/` | `.kiro/steering/*.md` |
| **OpenAI Codex** | `.codex/` | `AGENTS.md` |

---

## Quick Start

```bash
# 1) Clone the framework
git clone <this-repo> my-project && cd my-project

# 2) Edit the SSOT sources in hub/
#    - hub/project-context.md
#    - hub/memory/project-facts.md
#    - hub/mcp-servers.json

# 3) Synchronize all CLI targets
./sync.sh --fix

# 4) Launch your favorite tool
agy                   # Antigravity CLI
claude                # Claude Code
cursor .              # Cursor
```

---

## Framework Structure

UniCLI-Hub separates the **Framework Core** from your **Project Data**.

### 1. The Hub (`hub/`) — YOUR DATA
This is where you define the **Single Source of Truth**. **Edit these files.**
- `hub/agents/`: Canonical prompts for shared and specialized agents.
- `hub/skills/`: Custom skills (markdown + references).
- `hub/hooks/`: Shared Python hook logic.
- `hub/memory/`: Project facts, conventions, and glossary.
- `hub/mcp-servers.json`: Unified MCP configuration.
- `hub/project-context.md`: The "big picture" of your project.

### 2. The Core (`.unicli-hub/`) — FRAMEWORK LOGIC
Internal logic for fanning out assets. You rarely need to touch this.
- `scripts/`: Python renderers for Agents, Skills, Hooks, MCP, and Templates.
- `templates/`: Base templates for CLI entry points (`CLAUDE.md.tmpl`, etc.).

### 3. Derived Targets (Generated)
**Never edit these directly.** They are managed by `./sync.sh`.
- Root: `CLAUDE.md`, `AGENTS.md`.
- Tool Dirs: `.claude/`, `.agents/`, `.cursor/`, `.kiro/`, `.codex/`.

---

## The Rule: Edit Once, Sync Everywhere

1.  Modify your canonical source under `hub/`.
2.  Run `./sync.sh --fix`.
3.  The framework uses **Python-based guards** (`generated_file_guard.py`) to block accidental edits to derived files, redirecting you back to the `hub/`.

---

## Advanced Features

### Unified MCP Configuration
Edit `hub/mcp-servers.json` to define your tools (Tavily, JIRA, GitLab, etc.). Running `./sync.sh` will automatically configure them for all supported CLIs, including updating the `allowed` list for Antigravity.

### Specialized Agents
Drop a markdown prompt into `hub/agents/` and a `.kiro.json` metadata file. The framework will generate the corresponding agent for all five platforms.

---

## CI Integration

A `.pre-commit-config.yaml` is included. Install it to ensure no derived files drift in your commits:
```bash
pre-commit install
```
This runs `./sync.sh --check` before every commit.

---

*UniCLI-Hub: One Hub to rule them all.*
