# CTK Runbook

## Commands

```bash
# List available units
./scripts/run-tmf-ctk.sh --list

# Full matrix (stack already up — no --with-stack needed)
./scripts/run-tmf-ctk.sh --all

# Single unit (for targeted re-run after fix)
./scripts/run-tmf-ctk.sh --unit <unit-id>

# Aggregate results after run
REPORT_DIR=$(ls -td scripts/tmf-ctk/reports/*/ | head -1)
python3 scripts/aggregate-ctk-reports.py "$REPORT_DIR"
```

Config overrides: `scripts/tmf-ctk/.env.ctk` (gitignored). Example: `scripts/tmf-ctk/.env.ctk.example`.

## Unit registry and pass-rate thresholds

Source: `scripts/tmf-ctk/matrix.json`

| Unit ID | API | Service | Port | Min pass rate | Last known |
|---------|-----|---------|------|--------------|-----------|
| u02-tmf639-newman | TMF639 | resource-inventory | 8080 | ≥95% (268/268) | ✅ run-03 |
| u03-tmf634-newman | TMF634 | resource-catalog | 8082 | ≥90% | — |
| u04-tmf702 | TMF702 | change-management | 8083 | ≥95% | partial |
| u04-tmf641-newman | TMF641 | change-management | 8083 | 100% | — |
| u06-dr | DR | data-reconciliation | 8086 | ≥90% | — |
| u21-tmf632-newman | TMF632 | party-management | 8094 | ≥95% | ⚠️ 63.9% run-03 |
| u21-tmf673-newman | TMF673 | geographic-site | 8093 | ≥85% | — |
| u21-tmf674-newman | TMF674 | geographic-site | 8093 | 100% (217/217) | ✅ run-05 |

Note: u04-tmf702 requires the stack's internal Docker network; if `--with-stack` is not used, it may fail to reach `localhost:8083` via compose network. When running against a pre-started stack, plain `./scripts/run-tmf-ctk.sh --all` (without `--with-stack`) is correct.

## Report structure

```
scripts/tmf-ctk/reports/
└── <UTC-timestamp>/
    ├── summary.md                    ← aggregated pass/fail per unit
    └── <unit-id>/
        ├── summary.md                ← per-unit detail
        └── newman-output.json / test-output.txt
```

SSOT status docs:
- `specs/tmf/ctk/ctk-status-report.md` — historical run log (run-01..run-05)
- `specs/tmf/_summary.md` — static TMF judgement (run-13 as of 2026-05-21)

## Defect classification

| Condition | Priority | ID prefix |
|-----------|----------|-----------|
| Unit below min_assertion_pass_rate by >5% | P1 | CTK-* |
| Unit below threshold by ≤5% (marginal) | P2 | CTK-* |
| Unit passes but specific assertion group fails | P2 | CTK-* |
| Known regression from previous run | P1 | CTK-* |
| 100% pass (same as last known) | — (no defect) | — |
