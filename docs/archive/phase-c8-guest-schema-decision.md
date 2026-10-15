# Phase C+8 Guest Schema Decision

Date: 2026-07-14
Objects: `guest_messages`, `guest_message_bans`

## Ownership Record

| Field | Value |
|---|---|
| Schema owner | Unassigned; approval not evidenced |
| Business owner | Unassigned; approval not evidenced |
| Physical provenance | `UNKNOWN`; current database origin is not proven |
| Data compatibility | Not approved; prior read-only evidence recorded 8 guest messages and 0 bans |
| Retention decision | Not approved; IP/user-agent and message/ban retention remain unresolved |
| Alembic ownership | Not approved; no historical `create_table` record exists |

## Decision

```text
Decision B: explicitly excluded from the current migration scope
```

This is a scope exclusion, not a deletion decision and not proof that the tables are legacy or orphaned.

## Why the tables exist

Repository evidence shows active models, schemas, router registration, public create/list behavior, moderation, and ban queries. That proves runtime business usage. It does not prove whether the current database objects were created by `create_all`, manual DDL, external provisioning, or an omitted historical migration.

## Maintenance while excluded

- Preserve both tables and existing data.
- Keep their current runtime behavior under existing application ownership until a formal owner is assigned.
- Do not use `Base.metadata.create_all` as a production repair or provisioning mechanism.
- Do not generate a migration that retroactively asserts unproven provenance.
- Re-open the decision only after owner, provenance, data compatibility, retention, and Alembic ownership evidence is complete.

## Later handling

If the guest feature is retained, a future Option A baseline/provenance migration may be approved against the existing tables and data. If it is deprecated, a separate deprecation, export, retention, dependency, rollback, and removal plan is required. Deletion is not authorized.

## Closure status

Migration scope is excluded, but formal ownership and provenance remain `UNKNOWN`. The unresolved ownership prevents Migration Ready.
