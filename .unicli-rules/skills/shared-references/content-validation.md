# Content Validation Rules

## Before Creating ANY File

**MANDATORY**: Validate content before writing.

## Mermaid Diagram Validation

- Validate syntax before writing to any file
- Common issues: unclosed brackets, invalid node types, missing arrows
- Test with: paste into mermaid.live preview mentally or use a linter
- If unsure, use a simple flowchart style and avoid advanced features

## ASCII Art Standards

- Restrict to basic ASCII chars (no Unicode box-drawing)
- Provide a text-based alternative for complex visuals
- Max width: 80 characters per line

## Special Character Escaping

- In YAML frontmatter: escape double-quotes with `\"`
- In Markdown tables: escape pipes with `\|`
- In code blocks: use appropriate language tag for syntax highlighting

## Full Detail

See `.unicli-rules/common/content-validation.md` for complete rules.
See `.unicli-rules/common/ascii-diagram-standards.md` for ASCII rules.
