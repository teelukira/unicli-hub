# hub/plugins — CLI-Specific Plugins

Place per-CLI plugin directories here. Each subdirectory corresponds to one AI CLI target:

```
hub/plugins/
├── claude/     # Claude Code plugin files
├── cursor/     # Cursor plugin files
├── gemini/     # Gemini CLI plugin files
└── agy/        # Antigravity CLI plugin files
```

Plugin files are fanned out by `.unicli-hub/scripts/render_templates.py` via `./sync.sh --fix`.
