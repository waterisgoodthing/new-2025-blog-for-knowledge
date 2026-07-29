# C+3 Design

## Evidence model

Each decision is compared across four layers: current database metadata, SQLAlchemy model metadata, Alembic history, and runtime/documentation evidence. Repository intent is not treated as physical database provenance.

## Decision model

- Guest tables receive one formal classification from `official-schema`, `legacy-schema`, `orphan-schema`, or `unknown`, plus a separately stated operational disposition.
- Column drift decisions use only the four permitted values from the request.
- The index decision uses only the four permitted index actions from the request.
- Any unresolved provenance or semantics remains a gate blocker.

## Authority target

The target architecture is:

```text
Alembic migration -> database schema
```

Application startup may perform revision, readiness, and health checks, but must not provision schema. This is a future implementation design only.

## Evidence snapshot

- Alembic current revision: `018 (head)`.
- `backend/main.py:41-42` still runs `Base.metadata.create_all` during startup.
- Revision `005` creates `folders`, `notes.folder_id`, `notes.sort_order`, `idx_folders_sort_order`, and `idx_notes_folder_id`.
- Current SELECT metadata shows both guest tables, four nullable drift columns, and `idx_notes_folder_id`.
- Current NULL counts are zero for all four drift columns; this does not remove structural drift.
