# SID Schema Review

Cross-checks Flyway DDL + `sid-mapping.md` against MODA 25.5 via the TMF KB MCP.

## Step 1 — Run the local validator

```bash
python3 scripts/validate-sid-schema.py

# Per-unit targeted run
python3 scripts/validate-sid-schema.py --unit u02

# Reports land at:
ls -t specs/tmf/sid-schema/report-*.md | head -1        # deviation report
ls -t specs/tmf/sid-schema/seed-report-*.md | head -1   # seed data report
```

Supporting assets:
- `scripts/tmf-ctk/data-model/schemas/Resource/` — offline JSON Schema reference
- `docs/tmf-oracle/sid/moda-25.5-uml-xmi-index.md` — UML index
- `docs/tmf-oracle/openapi/api-directory.md` — API directory

## Step 2 — KB MCP cross-check for Resource domain

After local validation, cross-check each Resource ABE flagged in the report:

```
# Get the full Resource domain landscape from MODA 25.5
mcp__atom-tmf-kb-mcp__tmf_kb_get_domain_landscape({"domain": "Resource"})
```

For each entity the local script flags as divergent:
```
# 4-axis fidelity check: entity vs MODA 25.5 attribute
mcp__atom-tmf-kb-mcp__tmf_kb_judge({
  "candidate_id": "<entity-name>",
  "reverse_feature": "<attribute-name>"
})
```

To understand dependencies (e.g., which SID ABEs a given entity inherits from):
```
mcp__atom-tmf-kb-mcp__tmf_kb_graph_traverse({"node": "api:TMF639"})
```

For feature-vector search when the entity name is ambiguous:
```
mcp__atom-tmf-kb-mcp__tmf_kb_search_by_features({"feature_vector": ["administrativeState", "Resource", "lifecycle"]})
```

## Defect classification

| Deviation | Priority | SID-* ID |
|-----------|----------|----------|
| Mandatory ABE attribute missing from Flyway DDL | P1 | SID-* |
| Entity type in DDL contradicts MODA 25.5 type (e.g., `VARCHAR` vs `enum`) | P1 | SID-* |
| Attribute present but wrong cardinality (nullable vs required) | P2 | SID-* |
| Optional attribute missing | P3 | SID-* |
| Naming drift (SID uses `administrativeState`, DDL uses `admin_state`) | P3 | SID-* |

## Key domains to always review

- **Resource** (U02 TMF639): `Resource`, `ResourceRelationship`, `ResourceCharacteristic`
- **Resource Specification** (U03 TMF634): `ResourceSpecification`, `ResourceSpecCharacteristic`
- **Geographic Address** (U21 TMF673): `GeographicAddress`, `GeographicSubAddress`
- **Party / Organization** (U22 TMF632): `Organization`, `Individual`
