# Schema Remediation Approval Package

Date: 2026-07-14
Phase: C+4 Schema Remediation Approval Package
Status: approval preparation only; no implementation authorized.

## Current Authority State

Current architecture:

```text
Application startup Base.metadata.create_all
                         +
                 Alembic migration chain
                         =
              multiple schema authority
```

`backend/main.py` still invokes `Base.metadata.create_all` during startup. Alembic also owns a revision chain whose current database revision is `018 (head)`. `Base.metadata` is the model comparison source, but startup provisioning remains a second schema-affecting path.

Target architecture:

```text
Alembic migration
        |
        v
Database schema
```

Application startup should only perform read-only revision, readiness, and health checks.

## Remediation Scope

### Eligible for a future approved implementation

- Remove production startup `create_all`.
- Add a read-only startup readiness check for connectivity, Alembic revision, and schema compatibility.
- Establish an explicit, auditable metadata registry for Alembic target metadata.
- Design and execute approved migration remediation after semantic, data, backup, rollback, and verification reviews pass.

### Explicitly not approved in this package

- Guest table migration for `guest_messages` or `guest_message_bans`.
- Any nullable `ALTER COLUMN`, including setting columns `NOT NULL`.
- Deleting or recreating `idx_notes_folder_id`.
- Dropping either guest table.
- Any migration generation or execution.
- Any schema mutation caused by application startup.

## Risk Classification

### P0: must be resolved before Migration Ready

- Dual schema authority from startup `create_all` plus Alembic.
- Unknown physical provenance and ownership of `guest_messages` and `guest_message_bans`.
- Unresolved nullable semantics for `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order`.
- Unresolved authority policy for `idx_notes_folder_id`.
- Missing owner approval, data impact review, backup/restore evidence, rollback plan, and post-change verification plan.

### P1: design and implementation decisions required

- Explicit model metadata registry and deterministic import coverage.
- Startup readiness behavior and liveness/readiness separation.
- Development/test database and fixture provisioning path.
- Migration review workflow and drift verification gates.
- Guest retention/deprecation decision and compatible baseline migration strategy if accepted.

### P2: governance optimization

- Standardize schema inventory templates and decision records.
- Add recurring read-only drift checks to release review.
- Improve index workload evidence with query-plan and usage review.
- Maintain a schema owner and provenance register for future tables.

## Approval Checklist

| Approval item | Required decision/evidence | Status |
|---|---|---|
| Owner approval | Named owner accepts target schema and guest retention/deprecation path | Pending |
| Data impact review | Existing rows, NULL exposure, compatibility, export/retention impact | Pending |
| Backup plan | Pre-change backup scope, restore test/evidence, recovery point | Pending |
| Migration review | Reviewed Alembic design, ordering, lock/runtime impact, and verification hooks | Pending |
| Rollback plan | Reversible path or restore procedure; destructive actions separately approved | Pending |
| Verification plan | Revision, metadata, constraints/indexes, readiness, and application smoke checks | Pending |
| Deployment approval | Controlled production window and operator accountability | Pending |

## Approval rule

No P0 item may remain `UNKNOWN` when the gate is changed to Migration Ready. This package is a review input, not an execution authorization. Migration Gate remains `BLOCKED`.
