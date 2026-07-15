# Phase D Execution Scope

Date: 2026-07-15
Status: approval package preparation; implementation not started.

## Scope Source

This scope follows Phase C+13:

```text
Governance Decision = APPROVED
Migration Gate = READY_FOR_AUTHORIZATION
Phase D = AWAITING EXECUTION APPROVAL
```

## Allowed Files

These are planned files only. They are not modified in this phase.

| Planned file | Planned purpose | Current approval status |
|---|---|---|
| `backend/main.py` | Remove production `Base.metadata.create_all` schema mutation path and add read-only readiness validation. | Planned only |
| `backend/alembic/env.py` | Establish deterministic Alembic metadata authority and explicit model registry. | Planned only |
| `backend/app/models/note.py` | Align approved ORM metadata direction for `idx_notes_folder_id` only. | Planned only |
| `backend/alembic/versions/<new_revision>_metadata_authority_alignment.py` | Optional future reviewed migration file if the approved implementation requires one. | Planned only; not created |

Root `migration/` is not present in this repository and is not part of this planned scope.

## Allowed Operations

Allowed only after separate execution approval:

```text
remove Base.metadata.create_all production path
add read-only readiness validation
establish Alembic metadata registry
align approved ORM metadata
```

## Prohibited Operations

The following are excluded from Phase D execution scope unless a later governance review explicitly changes the boundary:

```text
guest schema changes
data migration
destructive operations
unapproved constraint changes
guest_messages
guest_message_bans
data cleanup
index deletion
```

## Current State

```text
Execution Scope = PREPARED
Authorization Status = NOT APPROVED
Implementation = NOT STARTED
```

No backend file, model file, migration file, database, DDL, or DML change was performed.
