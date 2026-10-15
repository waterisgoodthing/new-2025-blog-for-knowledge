# Guest Schema Final Decision Preparation

Date: 2026-07-14
Objects: `guest_messages`, `guest_message_bans`
Formal status: `UNKNOWN`
Decision mode: approval preparation only.

## 1. Are these formal business schema?

The evidence supports **active business behavior** but does not support a final `official-schema` classification. Models, schemas, router registration, and runtime queries are present. However, neither table has an Alembic `create_table` record, and current database provenance is not available. The correct formal boundary remains:

```text
runtime business usage = confirmed
formal migration-owned schema = UNKNOWN
physical database origin = UNKNOWN
```

They are not orphan tables because active routes and data access exist. They are not safely classifiable as legacy because no deprecation decision exists.

## 2. If accepted into official schema

The migration inclusion strategy is **Option A only after approval**. It must be a baseline/provenance migration designed against the existing database, not a clean-database assumption.

### Required migration baseline plan

1. Freeze and record the approved table contract for both tables.
2. Reconfirm current table existence, columns, defaults, nullability, primary keys, indexes, and foreign keys using read-only metadata queries.
3. Record the existing Alembic revision and database snapshot identifier.
4. Compare existing data with the accepted model contract; do not drop or recreate populated tables.
5. Design a migration that safely represents the already-existing objects, with explicit handling for environments where the tables do not exist.
6. Review generated SQL, lock/runtime behavior, idempotency assumptions, and rollback/restore path.
7. Execute only after owner, data, backup, migration, rollback, and verification approvals.

### Existing data compatibility

Prior read-only evidence recorded 8 rows in `guest_messages` and 0 rows in `guest_message_bans`. Compatibility review must cover message content, optional nickname/attachment fields, status values, timestamps, IP/user-agent retention, and ban expiry semantics. Existing data must be preserved unless an explicit retention/export decision says otherwise.

### Existing index and constraint inventory

The current model/database evidence records:

- `guest_messages`: primary key on `id`; indexes for status, `(attachment_type, attachment_slug)`, and `created_at`.
- `guest_message_bans`: primary key on `id`; an index on `ip_address`; nullable `reason` and `expires_at`; non-null `ip_address` and `created_at`.
- No guest-table foreign-key dependency is recorded in the reviewed evidence.

This is a planning baseline, not a substitute for a final pre-migration metadata SELECT and approval record.

## 3. If deprecated

Deletion is not selected and is not currently authorized. A future deprecation path would require:

1. product/owner decision to retire public guest messaging and moderation routes;
2. deprecation notice and a defined freeze date for new writes;
3. export of guest message and ban data with integrity verification;
4. retention/privacy decision for IP addresses and user agents;
5. dependency audit covering routers, schemas, frontend consumers, tests, and documentation;
6. a reviewed removal migration, backup, rollback/restore plan, and post-removal verification.

No deletion migration may be designed as an assumption from missing provenance.

## Final decision boundary

Current operational disposition: retain temporarily.
Formal schema classification: `UNKNOWN`.
Preferred future path if the feature is retained: approved Option A baseline/provenance migration.
Migration Gate: `BLOCKED`.
