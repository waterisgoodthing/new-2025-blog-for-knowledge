# Code Change Plan

Date: 2026-07-14  
Phase: C+5 implementation design only  
Status: no files changed.

## `backend/main.py`

### Current

The application lifespan calls `Base.metadata.create_all` during startup. This is an active schema-provisioning path and creates a second authority alongside Alembic.

### Future

Remove startup schema provisioning from the production path. Replace it with read-only readiness behavior that checks database connectivity, current Alembic revision, and application/schema compatibility. The process may remain alive but must not become ready when the schema is not approved or compatible.

Required review: deployment behavior, failure responses, liveness/readiness separation, local/test isolation, and rollback.

No change to `backend/main.py` is made in C+5.

## `backend/alembic/env.py`

### Current

Alembic uses `target_metadata = Base.metadata`, but model visibility depends partly on implicit package import side effects. The runtime inventory reaches 37 tables while migration history has 35 application `create_table` records; guest table provenance remains unresolved.

### Future

Introduce an explicit, auditable metadata registry at the model/Alembic boundary. It should intentionally import supported model modules, expose deterministic target metadata, avoid router/service imports and duplicate registration, and provide a table-by-table coverage record.

The registry must never call `create_all`. Guest tables enter the registry/migration coverage only after formal ownership and provenance approval.

Required review: clean-process inventory, import determinism, complete table coverage, Alembic comparison, and exclusion of bookkeeping objects from application coverage claims.

No change to `backend/alembic/env.py` is made in C+5.

## SQLAlchemy Models

The model layer may later need an explicit `idx_notes_folder_id` declaration if Candidate A from the index policy is approved. That change must be evaluated against the existing database index and Alembic autogenerate output.

The four nullable fields must not be changed until their business contracts are approved. Model typing alone is not schema authority, and current NULL count zero is not a `NOT NULL` decision.

Required review: API/runtime compatibility, historical data/write paths, metadata diff, tests, and migration impact.

No SQLAlchemy model is modified in C+5.

## Migration Files

Migration generation is allowed only after:

1. the relevant owner has approved the target contract;
2. guest provenance/ownership is closed if guest tables are in scope;
3. nullable and index decisions are explicit;
4. data impact, backup, rollback, and verification plans are approved;
5. generated SQL and operation ordering are reviewed;
6. a separate implementation authorization is recorded.

No migration file is generated or modified in C+5. No `alembic upgrade` or `alembic downgrade` is executed.
