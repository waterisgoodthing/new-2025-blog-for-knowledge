# Phase C+8 Nullable Contract Decision

Date: 2026-07-14
Mode: governance decision preparation; no nullable change authorized.

## Decision table

| Item | Decision |
|---|---|
| `folders.sort_order` Current DB | `integer`, nullable `YES`, default `0`; prior NULL count `0/2` |
| `folders.sort_order` ORM | `Integer`, inferred non-null, Python default `0` |
| `folders.sort_order` Business meaning | Active folder ordering, creation, update, reorder, and tree sorting |
| `folders.sort_order` Historical risk | Imports/future writes may omit values; current zero NULL count is not historical proof |
| `folders.sort_order` Owner | Unassigned; no approval record |
| `folders.sort_order` Target nullable state | Interim `KEEP NULLABLE`; final business contract `UNKNOWN` |
| `folders.sort_order` Migration required | No migration in current scope; future requirement `UNKNOWN` |
| `folders.created_at` Current DB | `timestamp without time zone`, nullable `YES`, default `now()`; prior NULL count `0/2` |
| `folders.created_at` ORM | `DateTime`, inferred non-null, server default `now()` |
| `folders.created_at` Business meaning | Folder creation lifecycle timestamp returned by the API |
| `folders.created_at` Historical risk | Imported or legacy rows may have different timestamp guarantees |
| `folders.created_at` Owner | Unassigned; no approval record |
| `folders.created_at` Target nullable state | Interim `KEEP NULLABLE`; final lifecycle contract `UNKNOWN` |
| `folders.created_at` Migration required | No migration in current scope; future requirement `UNKNOWN` |
| `folders.updated_at` Current DB | `timestamp without time zone`, nullable `YES`, default `now()`; prior NULL count `0/2` |
| `folders.updated_at` ORM | `DateTime`, inferred non-null, server default `now()`, model `onupdate` |
| `folders.updated_at` Business meaning | Folder modification lifecycle timestamp |
| `folders.updated_at` Historical risk | ORM/database update semantics and historical/import rows may diverge |
| `folders.updated_at` Owner | Unassigned; no approval record |
| `folders.updated_at` Target nullable state | Interim `KEEP NULLABLE`; final update contract `UNKNOWN` |
| `folders.updated_at` Migration required | No migration in current scope; future requirement `UNKNOWN` |
| `notes.sort_order` Current DB | `integer`, nullable `YES`, default `0`; prior NULL count `0/13` |
| `notes.sort_order` ORM | `Integer`, inferred non-null, Python default `0` |
| `notes.sort_order` Business meaning | Note create/update, filtering, folder ordering, and query ordering |
| `notes.sort_order` Historical risk | Unfoldered/imported notes may omit the field; tightening could reject future writes |
| `notes.sort_order` Owner | Unassigned; no approval record |
| `notes.sort_order` Target nullable state | Interim `KEEP NULLABLE`; final ordering contract `UNKNOWN` |
| `notes.sort_order` Migration required | No migration in current scope; future requirement `UNKNOWN` |

## Business justification and risk

The interim `KEEP NULLABLE` posture avoids an unapproved constraint change and preserves compatibility while contracts are unresolved. It is not based on NULL count alone and does not authorize changing ORM declarations or database constraints.

Any future `CHANGE TO NOT NULL` decision requires a named owner, business justification, historical/write-path review, data/backfill impact, reviewed migration, backup, rollback, and verification. None is complete.

## Closure status

No nullable migration is approved. The interim physical policy is `KEEP NULLABLE`; final contract ownership remains `UNKNOWN`. Migration Gate remains `BLOCKED`.
