# ADR Governance — Reference Pointer

Read `hub/extensions/adr/governance/adr-governance.md` for ADR Governance rules. Load ONLY when ADR Governance extension is Enabled (Full).

Key requirement: `**Relates-To-ADR**:` must be present in unit INDEX.md before Build and Test can proceed.

Key summary:
- Every `aidlc-docs/construction/{unit}/INDEX.md` must have a top-level `**Relates-To-ADR**:` line
- Format: `**Relates-To-ADR**: 0001, 0005, 0012` (comma-separated ADR numbers)
- If no ADRs apply, state explicitly: `**Relates-To-ADR**: N/A (no architectural decisions)`
- Missing or empty backlink = BLOCKING finding in Build and Test
- Verify backlinks before invoking tmf-compliance-reviewer or qa-tester
- The adr-index at `aidlc-docs/index/adr-index.md` is the lookup table
- adr-curator subagent drafts new ADRs in Nygard format when needed
- scripts/verify-adr-integrity.sh validates metadata + backlinks + supersede chain
