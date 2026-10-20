# Phase C+10 Guest Schema Evidence

Date: 2026-07-15
Objects: `guest_messages`, `guest_message_bans`

## Provenance evidence

| Required evidence | Current status |
|---|---|
| Creation source | `UNKNOWN`; no physical provisioning record |
| Alembic migration history | No `create_table` record found |
| Provisioning record | Missing |
| `create_all` attribution | Candidate only; not accepted as current database fact |

## Ownership evidence

| Required evidence | Current status |
|---|---|
| Schema owner | Unassigned |
| Business owner | Unassigned |
| Migration owner | Unassigned |

## Data evidence

| Required evidence | Current status |
|---|---|
| Row compatibility | Not approved; prior read-only evidence recorded 8 messages and 0 bans |
| Retention decision | Missing; message, ban, IP, and user-agent retention unresolved |
| Privacy impact | Missing |
| Index/constraint compatibility | Planning inventory exists; final pre-migration confirmation missing |

## Alembic ownership

Future Alembic ownership is not decided. If retained as official schema, an approved baseline/provenance migration must be designed against existing objects and data. If deprecated, a separate export, retention, dependency, rollback, and removal plan is required.

## Eligibility

```text
Guest Migration Eligibility = BLOCKED
```

No guest migration may be generated or executed without complete evidence. The tables remain excluded from any future migration scope until approved.
