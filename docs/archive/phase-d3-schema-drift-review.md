# Phase D-3 Schema Drift Review

Date: 2026-07-15
Mode: schema drift review; no remediation.

## ORM Metadata

Registry metadata import check confirmed:

```text
idx_notes_folder_id = True
```

The `notes` metadata includes:

```text
idx_notes_folder_id
idx_notes_next_review
idx_notes_search
idx_notes_status
ix_notes_slug
ix_notes_type
```

## Registry

Confirmed:

```text
GuestMessage = excluded
GuestMessageBan = excluded
has_guest_messages = False
has_guest_message_bans = False
```

## Constraints

The D-2 code change did not intentionally modify nullable contracts.

However, `alembic check` still detected nullable drift for:

```text
folders.sort_order
folders.created_at
folders.updated_at
notes.sort_order
```

That means the final execution gate is blocked until the metadata/database contract is reconciled or explicitly filtered/handled under an approved approach.

## Review Table

| Item | Result |
|---|---|
| Metadata alignment | `PARTIAL_PASS`: `idx_notes_folder_id` exists in ORM metadata. |
| Guest exclusion | `BLOCKED`: registry excludes guest schema, but Alembic autogenerate now proposes guest table/index removal. |
| Nullable unchanged | `BLOCKED`: D-2 did not change nullable intent, but Alembic still proposes unapproved nullable changes. |
| Index consistency | `PASS`: no `idx_notes_folder_id` deletion was detected. |

## Drift Decision

```text
Schema Drift Review = BLOCKED
```

No remediation was performed in Phase D-3.
