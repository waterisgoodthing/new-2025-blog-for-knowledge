# Phase D Nullable Drift Analysis

Date: 2026-07-15
Role: Database Migration Engineer
Mode: metadata repair; no database mutation.

## Approved Contract

Phase C+13 approved:

```text
APPROVED_KEEP_NULLABLE
```

for:

```text
folders.sort_order
folders.created_at
folders.updated_at
notes.sort_order
```

## Analysis

| Field | ORM | DB | Reason | Action |
|---|---|---|---|---|
| `folders.sort_order` | Previously implicit non-null from non-optional `Mapped[int]`; repaired to `nullable=True`. | Nullable. | Migration `005_add_folders.py` created the column without `nullable=False`; governance approved keeping NULL allowed. | Align ORM metadata to DB contract. No migration. |
| `folders.created_at` | Previously implicit non-null from non-optional `Mapped[datetime]`; repaired to `nullable=True`. | Nullable. | Migration `005_add_folders.py` created the column without `nullable=False`; governance approved keeping NULL allowed. | Align ORM metadata to DB contract. No migration. |
| `folders.updated_at` | Previously implicit non-null from non-optional `Mapped[datetime]`; repaired to `nullable=True`. | Nullable. | Migration `005_add_folders.py` created the column without `nullable=False`; governance approved keeping NULL allowed. | Align ORM metadata to DB contract. No migration. |
| `notes.sort_order` | Previously implicit non-null from non-optional `Mapped[int]`; repaired to `nullable=True`. | Nullable. | Migration `005_add_folders.py` added the column without `nullable=False`; governance approved keeping NULL allowed. | Align ORM metadata to DB contract. No migration. |

## Resolution

Selected option:

```text
A. Fix ORM metadata
```

Reason:

- The database nullable state matches the approved governance contract.
- The drift was caused by SQLAlchemy type annotation inference, not by an approved requirement to change constraints.
- Adjusting ORM metadata prevents Alembic from generating unauthorized `ALTER COLUMN` operations.

## Explicitly Not Performed

No migration was generated to change nullable constraints.

No `ALTER COLUMN SET NOT NULL` was executed.

No `ALTER COLUMN DROP NOT NULL` was executed.
