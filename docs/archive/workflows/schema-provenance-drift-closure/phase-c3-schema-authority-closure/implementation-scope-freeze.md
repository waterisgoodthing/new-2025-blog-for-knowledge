# Implementation Scope Freeze

Date: 2026-07-14
Phase: C+5 Implementation Readiness Review
Status: scope frozen for review; implementation not authorized.

## Approved Future Changes

The following items may enter a separately approved implementation phase:

- Remove production startup `Base.metadata.create_all`.
- Add read-only startup readiness checks for database connectivity, Alembic revision, and schema compatibility.
- Introduce an explicit, auditable metadata registry for Alembic target metadata.
- Execute approved schema migration remediation after owner, data, backup, rollback, migration review, and verification approvals.
- Establish explicit development/test database and fixture provisioning that cannot silently become production behavior.

These are scope permissions for future review, not authorization to edit files or execute commands in C+5.

## Deferred Changes

- Guest table migration until formal ownership, physical provenance, data compatibility, and migration baseline approval are complete.
- Nullable alteration for `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order` until each contract is approved.
- Index modification for `idx_notes_folder_id` until metadata policy and workload evidence are approved.
- Any model declaration change associated with the index until the resulting Alembic comparison is reviewed.
- Destructive/deprecation work until owner, export, retention, rollback, and dependency evidence exists.

## Forbidden Changes

- Delete `guest_messages` or `guest_message_bans`.
- Regenerate schema from `Base.metadata`.
- Silently generate a migration to make `alembic check` pass.
- Auto-create or auto-alter production schema at application startup.
- Execute `alembic upgrade` or `alembic downgrade` in this phase.
- Run `ALTER TABLE`, `DROP TABLE`, `DROP INDEX`, or any DDL/DML.
- Treat current code presence as proof of schema authority.
- Treat current NULL count zero as proof of `NOT NULL` semantics.

## Change Ownership Matrix

| Change | Owner | Evidence Required | Approval Status |
|---|---|---|---|
| Remove production startup `create_all` | Backend/platform owner | Current entrypoint audit, deployment impact, readiness behavior, rollback plan | Pending |
| Add startup readiness check | Backend/platform owner | Revision policy, health/readiness contract, failure behavior, smoke plan | Pending |
| Introduce explicit metadata registry | Backend/schema owner | Complete model inventory, deterministic import proof, Alembic target comparison | Pending |
| Guest table migration baseline | Guest feature/schema owner | Provenance evidence, owner decision, existing data compatibility, index/constraint inventory | Pending |
| Nullable contract remediation | Folder/note domain owner | Business semantics, historical/write-path review, NULL impact, backup and rollback plan | Pending |
| `idx_notes_folder_id` metadata policy | Notes/schema owner | Query path, workload/query-plan evidence, migration intent, autogenerate review | Pending |
| Any approved migration execution | Release/database operator | Reviewed migration, backup, restore test, rollback and verification evidence | Pending |

## Freeze result

The future implementation boundary is documented, but no change is approved for execution. Migration Gate remains `BLOCKED`.
