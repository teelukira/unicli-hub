# UI Sweep — Menu Inventory & CRUD Matrix

Source: `frontend/src/app/router.tsx` (40 routes, 15 top-level groups).

For each group below: navigate → snapshot → run CRUD steps → capture failures.
Quick mode covers groups 1–5 only.

---

## Group 1 — Dashboard
**Routes**: `/dashboard/equipment` · `/dashboard/reconciliation` · `/dashboard/alarm`
**CRUD**: None (view-only dashboards)
```
navigate → http://localhost:3000/dashboard/equipment
snapshot → verify KPI cards render with numbers (not 0/0/0 empty)
navigate → http://localhost:3000/dashboard/reconciliation
snapshot → verify DR status chart renders
navigate → http://localhost:3000/dashboard/alarm
snapshot → verify alarm table or "no alarms" state — not 500
```
Known issue FE-2: alarm proxy may be missing from nginx.conf — snapshot error rather than reporting CRUD fail.

---

## Group 2 — Resources (TMF639)
**Routes**: `/resources` · `/resources/new` · `/resources/:id` · `/resources/:id/edit`
**Backend**: `localhost:8080`
```
navigate → http://localhost:3000/resources
snapshot → verify resource list renders (≥1 row from IMOWN 50k seed)

# Create
click → "New Resource" or equivalent create button
fill form → name="mcp-ui-test-res-001", resourceStatus="standby", @type="Resource"
submit → verify redirect to detail page, ID in URL

# Read
snapshot → verify name, resourceStatus, @type fields present

# Update
click → Edit button
change name → "mcp-ui-test-res-001-edited"
save → verify updated value in detail view

# Delete
click → Delete button → confirm dialog → verify redirect to list, row gone
```

---

## Group 3 — Resource Catalogs (TMF634)
**Routes**: `/resource-catalogs` · `/resource-catalogs/new` · `/resource-catalogs/:id` · `/resource-catalogs/:id/edit`
**Backend**: `localhost:8082`
```
navigate → http://localhost:3000/resource-catalogs
snapshot → verify catalog/spec list renders

# Create ResourceSpecification
click → "New" button
fill → name="mcp-ui-spec-001", version="1.0"
submit → verify detail page

# Read + Edit + Delete (same pattern as Group 2)
```
Seed check: 12 resource categories should appear when navigating to categories sub-view (Physical, Equipment, Network, Location, Logical, Software, Service, Configuration, Radio, Transport, Core, Access).

---

## Group 4 — Change Orders (TMF641/702)
**Routes**: `/change-orders` · `/change-orders/new` · `/change-orders/:id`
**Backend**: `localhost:8083`
```
navigate → http://localhost:3000/change-orders
snapshot → verify order list (may be empty — OK)

click → "New Change Order"
fill → type/description fields
submit → verify order created with state=acknowledged

navigate to detail → verify Camunda Zeebe workflow state rendered
```
No edit/delete (state machine managed by Camunda).

---

## Group 5 — Zones (16 zone types)
**Routes**: `/zones` · `/zones/new` · `/zones/:id` · `/zones/:id/edit`
**Backend**: `localhost:8092`
```
navigate → http://localhost:3000/zones
snapshot → verify zone list with ≥16 seed rows

# CRUD golden path
click → "New Zone" → fill name="mcp-ui-zone-001", zoneType="COMMON"
submit → verify detail

edit → change description
delete → verify row gone
```
16 zone type seeds (COMMON, LTE, 5GX, BIZ, CAMPUS, SPEED, WZONE, TTL, DISTRICT, SCP, METRO, RURAL, INDOOR, OUTDOOR, CORE, EDGE) must be present on list page.

---

## Group 6 — Topology
**Route**: `/topology`
**Backend**: `localhost:8085` (Neo4j)
```
navigate → http://localhost:3000/topology
snapshot → verify graph canvas renders (or "no topology data" placeholder — not 500)
```
No CRUD from UI (read-only graph view).

---

## Group 7 — IPAM
**Routes**: `/ipam` · `/ipam/new` · `/ipam/:id` · `/ipam/:id/edit` · `/ipam/ipv6-pools` · `/ipam/allocations` · `/ipam/ipv6-allocations` · `/ipam/new-equipment-allocation`
**Backend**: `localhost:8084`
```
navigate → http://localhost:3000/ipam
snapshot → verify IP pool list

navigate → http://localhost:3000/ipam/allocations
snapshot → verify allocation table

# Create IP pool
navigate → http://localhost:3000/ipam/new
fill → cidrBlock or pool fields
submit → verify redirect to detail
```

---

## Group 8 — Network (FE-1 known issue)
**Routes**: `/network` (VPN Groups) · `/network/evc` · `/network/ovc` · `/network/data-links` · `/network/routes` + create sub-routes
```
navigate → http://localhost:3000/network
snapshot → verify VPN group list or ServiceComingSoonBanner
```
Known issue FE-1: `/api/v1/network/*` proxy entries may be missing from nginx.conf — expect 502 or banner. Record current state but do NOT record as new defect if it matches existing FE-1 description.

---

## Group 9 — Integration
**Routes**: `/integration/code-mappings` · `/integration/migration-jobs` · `/integration/field-mapping-rules`
**Backend**: `localhost:8081` (legacy-integration)
```
navigate → http://localhost:3000/integration/code-mappings
snapshot → verify mapping table (legacy code → canonical codes)

navigate → http://localhost:3000/integration/migration-jobs
snapshot → verify job list (may be empty)

navigate → http://localhost:3000/integration/field-mapping-rules
snapshot → verify rule list
```
These are configuration views — no create/delete from UI expected unless form exists.

---

## Group 10 — Data Collection
**Routes**: `/data-collection/jobs` · `/data-collection/schedules` · `/data-collection/parsers` · `/data-collection/pipeline`
**Backend**: `localhost:8087`
```
navigate → http://localhost:3000/data-collection/jobs
snapshot → verify job list

navigate → http://localhost:3000/data-collection/schedules
snapshot → verify schedule list

navigate → http://localhost:3000/data-collection/parsers
snapshot → verify parser config list

navigate → http://localhost:3000/data-collection/pipeline
snapshot → verify pipeline history table
```
No destructive CRUD (FTP/vendor collection jobs are admin-configured).

---

## Group 11 — Reconciliation
**Routes**: `/reconciliation/jobs` · `/reconciliation/:drSrno` (detail) · `/reconciliation/policies` · `/reconciliation/mapping-rules` · `/reconciliation/statistics` · `/reconciliation/sync-status` · `/reconciliation/process-history` · `/reconciliation/mismatch-overview`
**Backend**: `localhost:8086`
```
navigate → http://localhost:3000/reconciliation/jobs
snapshot → verify DR job list (may be empty if no reconciliation run yet)

navigate → http://localhost:3000/reconciliation/statistics
snapshot → verify stat charts render (not blank)

navigate → http://localhost:3000/reconciliation/mismatch-overview
snapshot → verify mismatch table or empty-state placeholder
```

---

## Group 12 — Geographic Sites (TMF674)
**Routes**: `/geographic-sites` · `/geographic-sites/new` · `/geographic-sites/:id` · `/geographic-sites/:id/edit`
**Backend**: `localhost:8093`
```
navigate → http://localhost:3000/geographic-sites
snapshot → verify site list

# CRUD
click → New → fill name, address fields
submit → verify detail
edit + delete (same as Group 2)
```

---

## Group 13 — Geographic Addresses (TMF673)
**Routes**: `/geographic-addresses` · `/geographic-addresses/new` · `/geographic-addresses/:id` · `/geographic-addresses/:id/edit`
**Backend**: `localhost:8093`
```
navigate → http://localhost:3000/geographic-addresses
snapshot → verify address list

# CRUD
POST via UI → streetName="Teheran-ro", city="Seoul"
verify detail → edit → delete
```

---

## Group 14 — Organizations (TMF632)
**Routes**: `/organizations` · `/organizations/new` · `/organizations/:id` · `/organizations/:id/edit`
**Backend**: `localhost:8094` (party-management-service)
```
navigate → http://localhost:3000/organizations
snapshot → verify org list

# CRUD
click → New → fill tradingName, @type="Organization"
submit → verify detail
PATCH → change tradingName → verify update
DELETE → verify row gone
```

---

## Group 15 — Audit Log
**Route**: `/audit`
```
navigate → http://localhost:3000/audit
snapshot → verify audit entry list renders with timestamps
```
Read-only view; no CRUD.
