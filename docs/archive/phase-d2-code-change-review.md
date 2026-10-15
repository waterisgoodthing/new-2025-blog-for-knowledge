# Phase D-2 Code Change Review

Date: 2026-07-15
Mode: approved code-layer refactor; no database migration.

## `backend/main.py`

### Before

Application lifespan opened an engine transaction and executed:

```text
Base.metadata.create_all
```

This allowed application startup to create missing schema objects.

### After

Application lifespan calls `validate_database_readiness()`.

The readiness validation is read-only:

```text
SELECT 1
SELECT version_num FROM alembic_version
```

It verifies that the expected Alembic revision `018` is present and raises if the database is not ready.

### Risk

- Environments that relied on startup auto-create must now initialize schema through explicit Alembic workflow.
- Startup now fails loudly when `alembic_version` is absent or not at the expected revision.
- This is intentional and keeps schema lifecycle outside application startup.

## `backend/alembic/env.py`

### Metadata Authority Change

Before:

```text
target_metadata = Base.metadata
```

with ad hoc model imports inside `env.py`.

After:

```text
from app.models.registry import SCHEMA_LIFECYCLE_METADATA
target_metadata = SCHEMA_LIFECYCLE_METADATA
```

The explicit registry owns the Alembic model-loading boundary.

## `backend/app/models/registry.py`

### Model Coverage

Created an explicit `MODEL_REGISTRY` with 34 schema-lifecycle models.

Explicitly excluded:

```text
GuestMessage
GuestMessageBan
guest_messages
guest_message_bans
```

The registry removes those guest tables from the lifecycle metadata if they were imported through package initialization.

## `backend/app/models/note.py`

### Index Metadata Alignment

Added ORM metadata for the existing database/migration index:

```text
Index("idx_notes_folder_id", "folder_id")
```

This aligns ORM metadata with the already-existing index from migration `005_add_folders.py`.

### Boundary

No `CREATE INDEX`, `DROP INDEX`, index rename, nullable change, or migration file was introduced.

## Summary

| File | Change | Risk |
|---|---|---|
| `backend/main.py` | Replaced runtime schema mutation with read-only readiness validation. | Startup now requires an initialized Alembic-managed database. |
| `backend/alembic/env.py` | Uses explicit registry metadata for Alembic target metadata. | Registry must remain current when adding approved schema-lifecycle models. |
| `backend/app/models/registry.py` | Added explicit schema-lifecycle model registry and guest exclusions. | Excluding guest schema is intentional; future guest schema work needs separate governance. |
| `backend/app/models/note.py` | Added `idx_notes_folder_id` ORM metadata. | Autogenerate must still be reviewed before execution; no migration required in this phase. |
