# C+3 Requirements

## R1 Guest ownership

Record model, router, schema, migration, documentation, and database evidence for `guest_messages` and `guest_message_bans`; classify their formal schema status without inferring authority from code presence alone.

## R2 Drift decisions

For `folders.sort_order`, `folders.created_at`, `folders.updated_at`, `notes.sort_order`, and `idx_notes_folder_id`, record current DB shape, model shape, migration intent, nullable/data evidence, business dependency, risk, and a permitted decision.

## R3 Authority transition

Document startup, development/test, and production deployment behavior for an Alembic-only target. The design must prohibit application-startup schema mutation in production.

## R4 Gate and validation

Record closed evidence, remaining unknowns, exact read-only validation activities, and the unchanged gate state. No migration, DDL, DML, or database write may be executed.

## Acceptance criteria

- Five requested reports exist in this task folder.
- Every requested object has evidence and a decision or explicit unknown status.
- The production sequence is `backup -> migration approval -> upgrade -> verification`.
- The final gate is `BLOCKED`.
