# ADR Governance — Opt-In

**Extension**: ADR Governance

## Opt-In Prompt

The following question is automatically included in the Requirements Analysis clarifying questions when this extension is loaded:

```markdown
## Question: ADR Governance Automation
Should the ADR governance automation (PR template enforcement, backlink check hook, CI verification) be enforced for this project?

A) Yes — enforce all ADR governance rules as blocking constraints (recommended for projects with active ADR-based SSOT)
B) No — skip ADR governance automation (suitable for ad-hoc projects or projects not using ADR)
C) Manual review only — keep ADR convention rules but do not activate automation/hooks (recommended for transition period)
X) Other (please describe after [Answer]: tag below)

[Answer]:
```

## Behavior

- **A (Full)**: All rules in `adr-governance.md` are enforced. `Relates-To-ADR` meta required in unit INDEX.md (`hooks/adr_backlink_check.py` PostToolUse 활성). PR/MR template enforced. CI verification (`verify-adr-integrity.sh`) blocking.
- **B (Disabled)**: Skip all rules in this extension.
- **C (Manual)**: Common rules in [`common/adr-conventions.md`](../../../common/adr-conventions.md) still apply (informational guide). Automation hooks/CI not wired.

Default for new sessions: **C (Manual)**, the transition state. Migrate to A after Phase 6 activation tasks complete.

Tracked in `aidlc-docs/aidlc-state.md` under `## Extension Configuration`:

```markdown
- ADR Governance: ✅ Enabled (Manual) | ❌ Disabled | ✅ Enabled (Full)
```
