# Phase D Migration Readiness Analysis

Date: 2026-07-15
Role: Database Migration Engineer
Mode: migration readiness repair; no database mutation.

## Problem

`alembic check` failed after Phase D-3 because Alembic autogenerate detected changes that are not authorized for execution:

- removal of `guest_messages`;
- removal of `guest_message_bans`;
- removal of guest-message indexes;
- nullable changes for approved keep-nullable fields.

## Guest Schema

Objects:

```text
guest_messages
guest_message_bans
```

Current understanding:

- The tables exist in the configured development database.
- Runtime code may still use the guest-message tables.
- Phase C+13 explicitly decided that these objects remain outside the current Alembic migration lifecycle.
- Exclusion is not deletion, deprecation, or data cleanup.

## Candidate Solutions

| Option | Description | Result |
|---|---|---|
| A | Alembic `include_object` exclusion for guest tables and related indexes. | Selected. Keeps physical tables untouched while preventing unauthorized drop operations in autogenerate. |
| B | Metadata isolation only. | Partial. Registry metadata already excludes guest tables, but reflected database-only tables still appear as removal candidates. |
| C | Re-add guest tables to Alembic lifecycle. | Rejected. This violates Phase C+13 guest scope decision. |
| D | Delete guest tables or indexes. | Rejected. DDL and guest data cleanup are prohibited. |

## Selected Approach

Implement Alembic autogenerate filtering in `backend/alembic/env.py`:

```text
include_object()
```

The filter excludes:

```text
guest_messages
guest_message_bans
```

and indexes attached to those tables.

## Expected Result

Alembic autogenerate must no longer propose:

```text
remove guest_messages
remove guest_message_bans
remove guest-message indexes
```

No guest schema migration is generated.

No guest schema DDL is executed.
