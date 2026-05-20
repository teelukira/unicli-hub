# Jira integration (code generation skill)

**Canonical rules:** read `.unicli-rules/common/jira-integration.md` in full (sections 0 through 5 and failure handling).

**This skill focus:** Construction — Code Generation. After Part 1 plan approval, ensure the unit has a real Jira key in the workflow state file, then transition to In Progress before Part 2 (see common doc section 3).

**Ticket creation SSOT:** primary creation runs at **Requirements Analysis** (see `aidlc-requirements-analysis` Step 10). If the Jira Ticket field is missing at Code Generation, follow common section 2 once (same preview plus `APPROVAL-JIRA-CREATE` gate). If a real project key already exists in state, do not create a duplicate — log `JIRA-REUSE` with the key and unit to the audit log and proceed.

**Description template SSOT:** `.unicli-rules/templates/remotes/jira-issue.body.md` — render with `scripts/render-ai-dlc-remote-templates.py` (see `.unicli-rules/templates/remotes/README.md`).
