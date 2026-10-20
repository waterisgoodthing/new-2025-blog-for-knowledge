# Alembic Authority Implementation Design

Date: 2026-07-14  
Status: design only; implementation deferred and gate-blocked.

## Target governance

```text
Approved schema intent
        |
        v
Approved Alembic revision
        |
        v
Database schema
        |
        v
Read-only application readiness check
```

The application must consume a schema produced by Alembic. `Base.metadata` remains a declarative comparison source, but it must not be an independent runtime provisioning authority.

## 1. `create_all` removal design

### Current risk

`backend/main.py` calls `Base.metadata.create_all` inside the application lifespan. At every startup, missing tables or compatible missing objects may be created outside the revision chain. This can hide missing migrations, produce environment-specific schema, and prevent reliable provenance attribution. The current database's presence of guest tables does not prove that startup created them.

### Future implementation shape

In a separately approved implementation phase:

- remove schema provisioning from the production lifespan;
- leave no fallback that calls `Base.metadata.create_all` when the revision is missing;
- make startup fail readiness when the database is unavailable or schema compatibility is not established;
- keep schema creation/provisioning in explicit migration or isolated fixture commands only;
- document a controlled local-development path that cannot be selected by production configuration.

No backend file is changed by this design document.

## 2. Startup readiness check design

Startup should perform read-only checks in this order:

1. establish a database connection;
2. execute a harmless connectivity query such as `SELECT 1`;
3. read the current Alembic revision from `alembic_version`;
4. compare it with the application-supported revision policy;
5. expose readiness only when the revision/schema compatibility check passes;
6. return a clear not-ready state when migration approval or execution is required.

The check must not call SQLAlchemy metadata creation, issue DDL, mutate `alembic_version`, or silently run upgrade/downgrade. Liveness and readiness should remain distinguishable: a process can be alive while not ready because schema prerequisites are unmet.

## 3. Explicit metadata registry design

### Current issue

Alembic `target_metadata = Base.metadata` currently reaches 37 tables through package import side effects. Direct and indirect imports are mixed, which makes coverage less explicit and makes it harder to prove that every model is intentionally included.

### Proposed design

Create an explicit, auditable registry at the model/Alembic boundary in a future approved implementation. The registry should:

- import every supported model module intentionally;
- expose one canonical `Base.metadata` target to Alembic;
- keep the model-to-migration coverage inventory reviewable by table;
- fail or flag missing registrations during static/check validation;
- avoid duplicate table registration and avoid importing application routers/services;
- distinguish supported application tables from bookkeeping such as `alembic_version`;
- record guest tables only after their formal ownership/provenance decision is approved.

The registry is a coverage/control mechanism, not a schema creation mechanism. It must not call `create_all`.

### Acceptance evidence for the future registry

- clean-process table inventory is deterministic;
- every supported model table has an explicit registry entry;
- Alembic `target_metadata` matches the registry;
- migration history coverage is reconciled per table;
- `alembic check` is clean after approved drift remediation;
- no startup path imports the registry for schema provisioning.

## 4. Migration-only governance flow

Every schema change should follow this controlled flow:

```text
read-only inventory
  -> owner decision
  -> data/backup impact review
  -> migration design
  -> migration approval
  -> backup / restore readiness
  -> controlled upgrade
  -> metadata and application verification
```

Governance rules:

- No model change without a matching schema decision and migration impact record.
- No migration generated merely to silence `alembic check` before semantic ownership is approved.
- No guest-table migration until provenance, ownership, and data impact are closed.
- No nullable change based solely on current zero-NULL counts.
- No index deletion or recreation without query/index risk review.
- Production application startup must never auto-create or alter schema.
- Downgrade or destructive actions require separate approval and backup/restore evidence.

## 5. Phase C+3 boundary

This document does not remove `create_all`, add an explicit registry, create a migration, execute Alembic, or modify the database. It defines the implementation contract for a later approved phase. Current authority therefore remains non-converged and Migration Gate remains `BLOCKED`.
