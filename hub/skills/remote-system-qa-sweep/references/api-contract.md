# API Contract Validation

Three-way diff: **runtime** `/v3/api-docs` ↔ **architect** `specs/tmf/u<NN>/api-spec.yaml` ↔ **TMF reference** `scripts/tmf-ctk/specs/<tmf>/*.oas.yaml`

## Commands

```bash
# Full three-way diff for all registered services
./scripts/validate-api-contract.sh --mode all

# Single service
./scripts/validate-api-contract.sh --mode runtime --service resource-inventory

# Spectral lint (static, no running stack needed)
npx spectral lint specs/tmf/u*/api-spec.yaml --ruleset scripts/.spectral.yaml 2>/dev/null || true
```

Verify API schema (additional check):
```bash
./scripts/verify-api-schema.sh 2>/dev/null || true
```

## Service registry

| Service | Port | Unit | Architect spec |
|---------|------|------|----------------|
| resource-inventory | 8080 | U02 | specs/tmf/u02/api-spec.yaml |
| resource-catalog | 8082 | U03 | specs/tmf/u03/api-spec.yaml |
| change-management | 8083 | U04 | specs/tmf/u04/api-spec.yaml |
| ipam-service | 8084 | U08 | specs/tmf/u08/api-spec.yaml |
| topology-service | 8085 | U10 | specs/tmf/u10/api-spec.yaml |
| zone-management | 8092 | U09 | specs/tmf/u09/api-spec.yaml |
| geographic-site-service | 8093 | U21 | specs/tmf/u21/api-spec.yaml |
| party-management-service | 8094 | U22 | specs/tmf/u22/api-spec.yaml |

## Report location

```
specs/tmf/api-contract/
└── <UTC-timestamp>/
    └── summary.md    ← deviations per service (runtime vs architect vs TMF ref)
```

## Defect classification

| Deviation | Priority | API-* ID |
|-----------|----------|----------|
| Required field missing from response | P1 | API-* |
| Wrong HTTP status code for standard operation | P1 | API-* |
| Response schema mismatch (type, format) | P2 | API-* |
| Extra undocumented fields in response | P2 | API-* |
| Naming/casing drift (camelCase vs snake_case) | P3 | API-* |
| Spectral lint warning | P3 | API-* |
