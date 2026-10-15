# Phase C+11 Guest Schema Resolution

Date: 2026-07-15
Objects: `guest_messages`, `guest_message_bans`

## Evidence Review

| Area | Current evidence | Resolution |
|---|---|---|
| Creation source | Runtime references exist; physical creation source is not established | `UNKNOWN` |
| Migration history | No Alembic `create_table` record was found | Unresolved |
| Provisioning evidence | No provisioning record supplied | Missing |
| Schema owner | No signed assignment | Missing |
| Business owner | No signed feature/data owner record | Missing |
| Compatibility | Prior read-only evidence recorded 8 messages and 0 bans; compatibility approval is absent | Unresolved |
| Retention/privacy | Retention, IP/user-agent handling, and privacy impact are not approved | Missing |
| Alembic ownership | No decision between baseline provenance and another governed disposition | Unresolved |

The existence of models, routers, or runtime references does not establish official schema ownership or database provenance. No current database source is assumed.

## Decision

```text
Guest Migration Eligibility = EXCLUDED_PENDING_OWNERSHIP
```

No guest migration, deletion, export, or retention change is authorized. To become `MIGRATION_ELIGIBLE`, the creation/provisioning source, owners, data compatibility, retention/privacy decision, and future Alembic owner must be documented and approved.
