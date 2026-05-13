# Core Workflow (Cursor Slim)

This is the **optimized always-on** Cursor rule. It provides high-level guidance while deferring to the canonical sources for full details.

## Adaptive Principle
The workflow adapts to the work: only execute stages that add value.

## The Three Phases (Mandatory)

1. **Explore** — Research the codebase and validate assumptions. Use `grep_search` and `glob` extensively.
2. **Plan** — Summarize the scope and approach. Obtain user approval for complex changes or architectural decisions.
3. **Execute** — Implement changes in small, verifiable steps. Update plan checkboxes immediately upon completion.

## Canonical Reference
For the full cross-CLI workflow definitions and governance rules, refer to:
- `.unicli-rules/core-workflow.md`

## Generated Paths
Do not edit derived files directly. Regenerate them using:
`./.unicli-rules/sync.sh --fix`
