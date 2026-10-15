# Phase D Implementation Authorization Draft

Date: 2026-07-14
Status: **DRAFT; NOT APPROVED**.
This document defines a possible future authorization boundary. It does not authorize code changes, migration generation, or database operations.

## Authorization prerequisites

Phase D may not begin until the C+6 checklist is complete, all P0 `UNKNOWN` items are resolved or explicitly excluded, and a named approver authorizes the exact file and migration scope.

## Allowed Future Changes

### `backend/main.py`

Allowed after approval:

- Remove production `Base.metadata.create_all` schema provisioning.
- Add read-only readiness checks for database connectivity, Alembic revision, and schema compatibility.
- Keep liveness separate from readiness and fail readiness without silently modifying schema.

### `backend/alembic/env.py`

Allowed after approval:

- Introduce an explicit metadata registry.
- Make model registration deterministic and auditable.
- Verify target metadata coverage table by table.
- Avoid router/service imports and any schema creation call.

### SQLAlchemy models

Only after separate approval may the model layer change for:

- an explicit `idx_notes_folder_id` declaration;
- a nullable contract change;
- any other schema-affecting declaration required by an approved target contract.

Model changes require matching migration review and compatibility verification. Current code presence is not authority evidence.

### Migration files

Only after approval may the team:

- generate a reviewed Alembic migration;
- include guest tables after ownership/provenance/data compatibility approval;
- include nullable changes after contract/data/rollback approval;
- include index metadata changes after policy/workload approval.

Migration SQL, ordering, backup, rollback, and verification must be reviewed before execution.

## Explicit exclusions

The draft does not authorize:

- guest table deletion;
- silent migration generation;
- schema regeneration from `Base.metadata`;
- production auto-create behavior;
- `alembic upgrade` or `alembic downgrade`;
- DDL or DML.

## Authorization record to complete later

| Field | Required value | Status |
|---|---|---|
| Approver | Named schema/release approver | Pending |
| Approved files | Exact backend/model/Alembic paths | Pending |
| Approved migration scope | Exact tables/columns/indexes | Pending |
| Backup evidence | Snapshot and restore evidence | Pending |
| Rollback owner | Named operator and procedure | Pending |
| Verification owner | Named verifier and checklist | Pending |
| Approval date/window | Controlled execution window | Pending |

Until this record is completed, Phase D remains unauthorized and Migration Gate remains `BLOCKED`.
