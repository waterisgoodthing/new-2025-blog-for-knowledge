# Schema Authority Closure Decision

Date: 2026-07-14  
Decision: `BLOCKED`

## Closed items

- Migration inventory and current revision check completed: `018 (head)`.
- Schema coverage and provenance evidence reviewed for the guest tables.
- Current database metadata SELECT completed for target tables, columns, indexes, and NULL counts.
- Drift matrix completed for the four columns and `idx_notes_folder_id`.
- Guest ownership disposition documented without claiming unsupported official status.
- Alembic-only transition architecture documented for startup, development/test, and production.
- Forbidden-operation boundary recorded and preserved.

## Remaining unknown

### Unresolved provenance

- Physical provisioning origin of `guest_messages` and `guest_message_bans`.
- Whether the guest feature has an approved long-term product/schema owner.
- Whether any external or historical source exists outside the repository evidence inspected here.

### Unresolved semantic decisions

- NULL versus non-NULL contract for `folders.sort_order`.
- NULL versus non-NULL contract for `folders.created_at`.
- NULL versus non-NULL contract for `folders.updated_at`.
- NULL versus non-NULL contract for `notes.sort_order`.
- Approved model metadata policy for `idx_notes_folder_id`.
- Production implementation and rollout approval for removing startup `create_all`.

## Gate decision

`BLOCKED`

The package is ready for human review, but not ready for migration execution or schema authority closure. No deliverable in this folder authorizes a migration, DDL, DML, index change, nullable change, table deletion, or startup behavior change.
