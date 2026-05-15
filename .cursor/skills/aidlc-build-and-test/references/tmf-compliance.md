# TMF Compliance — Reference Pointer

Read `.unicli-rules/extensions/tmf/compliance/tmf-compliance.md` for the full 14-rule TMF compliance matrix (TMF-A through TMF-N). Load this file ONLY when TMF Compliance extension is Enabled.

Rules TMF-A/B/C/D/E/F/G/H/I/J/K/L/M/N are detailed there.

Key summary:
- TMF-A: API naming conventions (TMF Open API standard)
- TMF-B: Resource representation (SID GB922 alignment)
- TMF-C: HTTP method semantics (GET/POST/PATCH/DELETE correctness)
- TMF-D: Response codes (correct use of 200/201/204/400/404/422/500)
- TMF-E: Pagination (fields: totalResults, totalPages, offset, limit)
- TMF-F: Filtering (fieldsParam, query attributes)
- TMF-G: Notification/event schema (TMF688 compliant)
- TMF-H: Hypermedia (@referredType, href)
- TMF-I: Mandatory fields (id, href, @type)
- TMF-J: Polymorphism (@type/@schemaLocation/@baseType)
- TMF-K: Partial update (PATCH with JSON Merge Patch)
- TMF-L: Error response schema (TroubleTicket pattern)
- TMF-M: API versioning (/tmf-api/v5/...)
- TMF-N: CTK runtime conformance (Newman test pass)

The tmf-compliance-reviewer subagent uses the atom-tmf-kb-mcp tools to verify each rule.
