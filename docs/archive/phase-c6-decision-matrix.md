# Phase C+6 Decision Matrix

Date: 2026-07-14
Status: approval preparation only; `Migration Gate = BLOCKED`.

## 1. Guest Schema Ownership Decision

Formal ownership remains `UNKNOWN`. Runtime business usage is confirmed, but code presence does not prove schema authority or physical database provenance.

| Item | Current state | Required evidence | Recommended decision | Enter migration? |
|---|---|---|---|---|
| `guest_messages` | Model/router/schema/database presence confirmed; physical provenance `UNKNOWN`; prior read-only count 8 rows | Physical provenance, named owner, existing data compatibility, accepted migration ownership, index/constraint inventory | Retain temporarily; if business feature is retained, approve Option A baseline/provenance migration against existing data | No, until all evidence and owner approval exist |
| `guest_message_bans` | Model/router/database presence confirmed; physical provenance `UNKNOWN`; prior read-only count 0 rows | Physical provenance, named owner, ban-data retention decision, compatibility, migration ownership, index/constraint inventory | Retain temporarily; include only in a later approved guest baseline decision | No, until all evidence and owner approval exist |

### Required guest evidence

- **Physical provenance:** current database creation source or approved provisioning/audit evidence. `create_all` remains only a documented candidate, not a fact.
- **Owner:** named business/schema owner for guest messages and moderation bans.
- **Existing data compatibility:** content, optional fields, status, timestamps, IP/user-agent retention, expiry semantics, and export/privacy impact.
- **Migration ownership:** explicit decision whether these objects become official Alembic-owned schema or are deprecated through an approved removal process.

No guest table may be deleted or silently migrated from missing provenance.

## 2. Nullable Contract Decision

Current NULL counts are zero, but that does not establish `NOT NULL` semantics. Each field remains `UNKNOWN` until business semantics, write paths, historical data, and owner approval are complete.

| Field | Current database state | ORM declaration | API/write path | Historical data risk | Migration decision |
|---|---|---|---|---|---|
| `folders.sort_order` | `integer`, nullable `YES`, default `0`; prior NULL `0/2` | `Integer`, inferred non-null, Python default `0` | Folder creation, update, reorder, and tree sorting use the field | Future/imported NULL rows may be rejected by a constraint change; current zero count is insufficient | `UNKNOWN`; no migration until ordering/nullability contract approved |
| `folders.created_at` | `timestamp without time zone`, nullable `YES`, default `now()`; prior NULL `0/2` | `DateTime`, inferred non-null, server default `now()` | Returned in folder output; lifecycle/import semantics not fully approved | Historical/import rows and timestamp contract may differ | `UNKNOWN`; preserve current DB state pending owner decision |
| `folders.updated_at` | `timestamp without time zone`, nullable `YES`, default `now()`; prior NULL `0/2` | `DateTime`, inferred non-null, server default `now()`, model `onupdate` | Returned in folder output and model update lifecycle | Database-side and ORM update semantics may diverge; unseen historical NULL risk | `UNKNOWN`; no direct NOT NULL recommendation |
| `notes.sort_order` | `integer`, nullable `YES`, default `0`; prior NULL `0/13` | `Integer`, inferred non-null, Python default `0` | Note create/update, filtering, and ordering use the field | Unfoldered/imported notes may omit the field; tightening could break writes | `UNKNOWN`; future migration only after contract approval |

## 3. Index Policy Decision

Object: `idx_notes_folder_id`

- **Current database index:** non-unique btree on `notes(folder_id)`.
- **ORM metadata:** `Note.folder_id` exists, but `Note.__table_args__` omits the index.
- **Alembic diff risk:** `alembic check` reports the physical index as removed from model metadata; deleting it would contradict revision `005` creation intent and may affect folder-scoped lookup.
- **Query evidence:** folder-scoped note paths filter by `Note.folder_id`; query-plan/workload evidence was not collected, so performance criticality remains `UNKNOWN`.

### Candidates

- **Candidate A:** preserve the database index and later add an explicit model metadata declaration after approval.
- **Candidate B:** preserve the historical physical index without expressing it in ORM metadata, with an explicit governance exception.
- **Candidate C:** delete the index. This is not approved and requires workload, rollback, and owner evidence.

### Recommendation

Recommend **Candidate A in principle**, with the only current action being preservation of the existing index. No deletion, recreation, or model change is authorized in C+6.

## Decision status

All unresolved ownership and semantic items remain `UNKNOWN`. No item enters migration scope in C+6.
