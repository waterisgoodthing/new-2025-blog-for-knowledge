# Phase D-1 Pre-Draft Analysis

Date: 2026-07-15
Mode: migration draft preparation; no execution.

## Current State

### Current Alembic Head

Phase C evidence records the target database at Alembic `018 (head)`. Phase D-1 did not run Alembic or connect to the database, so this was not revalidated live in this phase.

File inspection shows the main revision chain reaches:

```text
018_add_ai_runs.py
revision: 018
down_revision: 017
```

The version directory also contains older non-numeric revision files:

```text
0ec85724afb9_add_user_admin_field.py
1119bee5a419_add_images_to_notes.py
```

`003_restore_notes_status_index.py` points to `1119bee5a419`, so the file-level revision graph must be validated by Alembic before any execution approval. This phase did not execute that validation.

### Current Migration List

Inspected migration files:

```text
001_initial_schema.py
002_add_status_field.py
003_restore_notes_status_index.py
004_add_ai_metadata_to_notes.py
005_add_folders.py
006_add_admin_sessions.py
007_change_folder_cascade.py
008_add_audit_logs.py
009_add_music_daily.py
010_add_managed_content_entries.py
011_add_subject_taxonomy.py
012_add_question_drafts_and_questions.py
013_add_mistakes_and_review.py
014_add_attachments.py
015_add_capture_items.py
016_add_ai_call_logs.py
017_add_prompt_version.py
018_add_ai_runs.py
0ec85724afb9_add_user_admin_field.py
1119bee5a419_add_images_to_notes.py
```

Relevant existing migration evidence:

- `005_add_folders.py` creates `idx_notes_folder_id` on `notes(folder_id)`.
- `005_add_folders.py` downgrade drops `idx_notes_folder_id`.
- No Phase D-1 migration file was generated.

### Current Model Metadata

Observed source facts:

- `backend/main.py` imports `Base` and executes `await conn.run_sync(Base.metadata.create_all)` inside application lifespan.
- `backend/alembic/env.py` sets `target_metadata = Base.metadata`.
- `backend/alembic/env.py` explicitly imports several model modules, but the registry is not presented as a single auditable model registry object.
- `backend/app/models/note.py` defines `Note.__table_args__` with:
  - `idx_notes_status`
  - `idx_notes_next_review`
  - `idx_notes_search`
- `backend/app/models/note.py` does not currently declare `idx_notes_folder_id`.

### Current Database State

No live database command, SQL command, Alembic command, DDL, or DML was executed in Phase D-1.

Database state is therefore recorded from prior governance evidence only:

- Prior Phase C evidence recorded the target database at `018 (head)`.
- Prior Phase C evidence recorded `idx_notes_folder_id` as physically present.
- Prior Phase C evidence recorded nullable drift for `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order`.

These facts must be revalidated before execution.

## Boundary

```text
Database operation = NONE
DDL execution = NONE
DML execution = NONE
alembic upgrade = NONE
alembic downgrade = NONE
```
