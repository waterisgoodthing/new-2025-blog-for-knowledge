# Phase C+9 Migration Scope Decision

Date: 2026-07-15
Status: scope prepared, not approved for execution.

## Included

The following are eligible for a future explicitly approved Phase D implementation scope:

- remove production startup `Base.metadata.create_all`;
- add read-only startup readiness checks;
- introduce an explicit Alembic metadata registry;
- generate and execute only separately approved schema remediation.

These are future scope candidates, not current authorization.

## Excluded

- `guest_messages` migration;
- `guest_message_bans` migration;
- nullable changes for `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order`;
- `idx_notes_folder_id` deletion, recreation, or unapproved model declaration;
- any destructive guest-table operation;
- any silent migration generation;
- any production schema auto-creation.

## Unknown

- Guest physical provenance and formal schema/business ownership.
- Guest data compatibility, retention, and Alembic ownership.
- Final nullable contracts and owners for all four fields.
- Final index policy, owner, and workload evidence.
- Exact approved migration object set.

## Scope rule

No `UNKNOWN` object may be automatically moved into migration scope. The only current migration scope decision is that guest tables, nullable changes, and index changes remain excluded. Migration Gate remains `BLOCKED`.
