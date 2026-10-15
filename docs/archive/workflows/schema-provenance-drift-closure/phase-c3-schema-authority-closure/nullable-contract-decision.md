# Nullable Contract Decision

Date: 2026-07-14
Mode: semantic approval preparation; no nullable change authorized.

## Decision rule

Current NULL counts are zero, but `NULL = 0` is not evidence that a column should become `NOT NULL`. The recommendation for every field below is to preserve the current database state while the owner-approved contract remains unresolved. A future migration is required only if the approved target differs from the current database contract.

## Field decisions

### `folders.sort_order`

- **Current DB state:** `integer`, nullable `YES`, default `0`; prior count `0/2` NULL.
- **Current Model state:** `Integer`, inferred non-null, Python default `0`, no explicit server default.
- **Migration history:** revision `005` creates the column with server default `0` and omits `nullable`.
- **Business meaning:** folder ordering is actively read, assigned, updated, and used for tree ordering.
- **Recommended target state:** preserve database `nullable YES` pending owner decision; document the ordering contract explicitly. Do not infer `NOT NULL` from the current count.
- **Risk:** changing nullability could reject historical/future writes or diverge from API/runtime assumptions; preserving the difference keeps autogenerate drift visible.
- **Needs migration:** `UNKNOWN` until the owner approves the nullable contract. If the approved target differs, design a reviewed migration with data/backfill handling.

### `folders.created_at`

- **Current DB state:** `timestamp without time zone`, nullable `YES`, default `now()`; prior count `0/2` NULL.
- **Current Model state:** `DateTime`, inferred non-null, server default `now()`.
- **Migration history:** revision `005` creates DateTime with `now()` and omits `nullable`.
- **Business meaning:** creation timestamp is returned with folder data and participates in the model lifecycle; the reviewed evidence does not define whether imported/legacy rows may omit it.
- **Recommended target state:** preserve database `nullable YES` until lifecycle/import semantics and timestamp contract are approved.
- **Risk:** forcing non-null may break imports or historical rows; making the model nullable may weaken typed/API assumptions.
- **Needs migration:** `UNKNOWN`; only if approved contract differs from current database state.

### `folders.updated_at`

- **Current DB state:** `timestamp without time zone`, nullable `YES`, default `now()`; prior count `0/2` NULL.
- **Current Model state:** `DateTime`, inferred non-null, server default `now()`, with model `onupdate` behavior.
- **Migration history:** revision `005` creates DateTime with `now()` and omits `nullable`.
- **Business meaning:** update timestamp represents folder modification lifecycle, but the reviewed migration does not settle nullable or update semantics for all historical paths.
- **Recommended target state:** preserve database `nullable YES` pending an approved lifecycle contract and write-path review.
- **Risk:** a constraint change can fail on unobserved historical/import data; model/runtime update behavior may not match database-side behavior.
- **Needs migration:** `UNKNOWN`; no direct `ALTER COLUMN SET NOT NULL` recommendation.

### `notes.sort_order`

- **Current DB state:** `integer`, nullable `YES`, default `0`; prior count `0/13` NULL.
- **Current Model state:** `Integer`, inferred non-null, Python default `0`, no explicit server default.
- **Migration history:** revision `005` adds the column with server default `0` and omits `nullable`.
- **Business meaning:** note ordering is accepted, filtered, and used for ordering in folder/note query paths.
- **Recommended target state:** preserve database `nullable YES` until ordering semantics for foldered and unfoldered notes are explicitly approved.
- **Risk:** tightening the constraint can affect imports, older rows, or clients that omit the field; preserving the difference leaves model/database drift unresolved.
- **Needs migration:** `UNKNOWN`; require a future reviewed migration only after contract approval.

## Required approval evidence

- Named owner for content/folder semantics.
- Read-only historical NULL and write-path review beyond the current row counts.
- API/fixture/import compatibility review.
- Approved choice between database-nullable, model-non-null, or another documented contract.
- Data/backfill, backup, rollback, and verification plan if a migration is approved.

Migration Gate remains `BLOCKED`.
