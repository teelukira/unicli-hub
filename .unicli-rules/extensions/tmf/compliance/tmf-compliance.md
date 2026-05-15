# TMF Compliance Rules

## Overview

These TMF compliance rules are MANDATORY cross-cutting constraints that apply
across AI-DLC Construction phases when building TMF-standard services.
They are hard constraints that stages MUST enforce when generating code.

**Enforcement**: At each applicable stage, the model MUST verify compliance
before presenting the stage completion message.

### Blocking Finding Behavior

A **blocking TMF finding** means:
1. The finding MUST be listed under a "TMF Compliance Findings" section
2. The stage MUST NOT present "Continue to Next Stage" until resolved
3. Only "Request Changes" is available until all blocking findings clear
4. The finding MUST be logged in `aidlc-docs/audit.md`

---

## Rule TMF-01: Architect Spec Prerequisite

**Rule**: Before Code Generation for any TMF-standard unit, the TMF Architect subagent
MUST have produced spec artifacts:
- `specs/tmf/{unit}/api-spec.yaml` MUST exist
- `specs/tmf/{unit}/sid-mapping.md` MUST exist

**TMF-standard units** are those that implement a TMF Open API specification:
U02 (TMF639), U03 (TMF634), U04 (TMF641/702), U08 (TMF639), U10 (TMF639).

**SKT proprietary extensions** (units carrying an SKT-TMFC-XXX component code,
such as U05 SKT-TMFC-003/004/005, U06 SKT-TMFC-006, U07 SKT-TMFC-007) are
**NOT TMF-standard** and are **excluded from TMF-01 through TMF-10**.
These units do not require TMF Architect specs or Compliance Reviewer invocation.

**Verification**:
- Check file existence before starting code generation
- If missing for a TMF-standard unit, prompt user to run TMF Architect first
- If unit is SKT-TMFC-XXX: skip TMF-01 through TMF-10 entirely, log N/A in audit.md

---

## Rule TMF-02: DTO Schema Match

**Rule**: Every TMF DTO class MUST have fields that 100% match the
corresponding schema in `specs/tmf/{unit}/api-spec.yaml`.

**Verification**:
- No missing fields (in spec but not in DTO)
- No extra fields (in DTO but not in spec, unless `skt_` prefixed)
- Types match (string->String, integer->Int, number->BigDecimal)
- Required fields have `@field:NotNull`

---

## Rule TMF-03: SID Entity Naming

**Rule**: JPA entity class names MUST match SID ABE names as defined in
`specs/tmf/{unit}/sid-mapping.md`.

**Verification**:
- Entity name appears in sid-mapping.md
- No legacy or ad-hoc naming (Equipment, Device, Site)

---

## Rule TMF-04: eTOM State Machine

**Rule**: Resource lifecycle state enums MUST include TMF-standard values
and state transitions MUST follow the allowed matrix.

**Verification**:
- Enum includes: PLANNING, INSTALLING, OPERATING, RETIRING
- No invalid transitions (e.g., PLANNING->OPERATING directly)
- State changes publish `ResourceStateChangeEvent`

---

## Rule TMF-05: TMF Event Naming

**Rule**: Event classes MUST follow TMF naming convention.

**Verification**:
- `{Resource}CreateEvent` exists
- `{Resource}AttributeValueChangeEvent` exists
- `{Resource}StateChangeEvent` exists
- `{Resource}DeleteEvent` exists
- Each event has: eventId, eventTime, eventType, event payload

---

## Rule TMF-06: TMF Error Response

**Rule**: Error responses MUST use TMF error structure.

**Verification**:
- Error DTO has: code, reason, message fields
- Exception handlers return this structure
- HTTP status codes are set correctly

---

## Rule TMF-07: TMF Pagination

**Rule**: List endpoints MUST support TMF pagination.

**Verification**:
- `offset` and `limit` query parameters present
- `X-Total-Count` response header set
- Default values: offset=0, limit=20

---

## Rule TMF-08: SKT Extension Isolation

**Rule**: SKT-specific fields MUST be isolated from TMF standard DTOs.

**Verification**:
- `skt_` prefix on all non-standard DB columns
- Extension fields in separate DTO classes (`dto/skt/`)
- TMF standard DTOs in `dto/tmf/` contain only spec fields

---

## Rule TMF-09: SSoT Data Ownership

**Rule**: Each SID entity MUST be owned by exactly one microservice.

**Verification**:
- No `@Entity` class duplicated across services
- Entity ownership matches `specs/tmf/{unit}/sid-mapping.md`

---

## Rule TMF-10: Compliance Review Required

**Rule**: After Code Generation completes for a TMF-standard unit, the TMF Compliance
Reviewer subagent MUST be executed (during Build and Test stage) before the unit
can be marked complete.

**Verification**:
- `specs/tmf/{unit}/review-report.md` exists
- Review report verdict is PASS (0 BLOCKING findings)
- If FAIL, iterate: fix findings -> re-review until PASS

**For non-TMF-standard units (SKT-TMFC-XXX)**: This rule is N/A.
Record the skip rationale in `audit.md`: `TMF reviewer skipped — non-standard SKT extension ({unit} = {SKT-TMFC-XXX code})`

---

## Stage Applicability

| Stage | Applicable Rules |
|-------|-----------------|
| Functional Design | TMF-03, TMF-04 |
| NFR Requirements | N/A |
| NFR Design | N/A |
| Infrastructure Design | N/A |
| Code Generation | TMF-01 through TMF-10 (all) |
| Build and Test | TMF-10 (invoke tmf-compliance-reviewer, verify PASS) |

---

## Unit Applicability

| Unit | TMF Standard | SKT-TMFC-XXX | Reviewer Required |
|------|-------------|--------------|-------------------|
| U02 (Resource Inventory, TMF639) | yes | — | mandatory |
| U03 (Resource Catalog, TMF634) | yes | — | mandatory |
| U04 (Change Management, TMF641/702) | yes | — | mandatory |
| U08 (IPAM, TMF639) | yes | — | mandatory |
| U10 (Topology, TMF639) | yes | — | mandatory |
| U05 (Data Collection) | no | SKT-TMFC-003/004/005 | N/A |
| U06 (Data Reconciliation) | no | SKT-TMFC-006 | N/A |
| U07 (Legacy Integration Hub) | no | SKT-TMFC-007 | N/A |
| U01 / U01-DB (Infrastructure) | no | — | N/A |
| U11 / U11-Full (Frontend) | no | — | N/A |
| U12 (Auth Governance) | no | — | N/A |
| U99 (TMF Re-verification) | meta | — | N/A |
