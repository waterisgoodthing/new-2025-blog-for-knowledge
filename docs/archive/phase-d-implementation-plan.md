# Phase D Implementation Plan

Date: 2026-07-15
Status: plan only; not executed.

## Step 1 - `backend/main.py`

Planned target:

- Remove production startup schema mutation through `Base.metadata.create_all`.
- Preserve application startup behavior without silently creating or mutating schema.
- Add read-only readiness validation for database connectivity and expected migration state.
- Keep readiness failure visible without running upgrade, downgrade, DDL, or DML.

Execution constraints:

- No database mutation from application startup.
- No Alembic execution inside application startup.
- Liveness and readiness should remain separate.

## Step 2 - `backend/alembic/env.py`

Planned target:

```text
deterministic metadata authority
```

Requirements:

- Use explicit model imports or an explicit registry with auditable coverage.
- Define `target_metadata` from the approved metadata authority.
- Avoid implicit package scanning as the only coverage mechanism.
- Avoid router/service imports.
- Avoid schema creation calls.

Expected review evidence before execution:

- Table coverage list.
- Index coverage list.
- Constraint coverage list.
- Clear explanation of any intentional exclusions.

## Step 3 - Model Metadata Alignment

Approved object only:

```text
idx_notes_folder_id
```

Planned target:

- Align ORM metadata with the existing database/Alembic index direction.
- Preserve the existing index.
- Do not delete or recreate the index without separate approval.

Explicit prohibition:

```text
Do not change nullable contracts in this step.
```

The nullable contract decision is `APPROVED_KEEP_NULLABLE`; it does not authorize converting fields to `NOT NULL`.

## Step 4 - Migration Review

If a migration is required, it must be reviewed before execution.

Required review:

- Exact objects.
- Generated or handwritten SQL.
- Downgrade behavior.
- Impact on existing data.
- Rollback strategy.
- Validation commands.
- Stop conditions.

Migration review must not include:

- `guest_messages`.
- `guest_message_bans`.
- data cleanup.
- destructive migration.
- unapproved nullable changes.
- index deletion.

## Current Status

```text
Implementation Plan = PREPARED
Execution Authorization = NOT APPROVED
Implementation = NOT STARTED
```
