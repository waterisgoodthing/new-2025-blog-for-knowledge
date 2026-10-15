# Phase C+13 Nullable Contract Approval

Date: 2026-07-15
Decision: `APPROVED_KEEP_NULLABLE`

## Fields

```text
folders.sort_order
folders.created_at
folders.updated_at
notes.sort_order
```

## Approval

| Field | Owner approval | Business interpretation | Decision | Future review condition |
|---|---|---|---|---|
| `folders.sort_order` | Project Owner | Folder ordering may continue to tolerate the current nullable database contract. | `APPROVED_KEEP_NULLABLE` | Revisit if product requirements require strict non-null ordering or if write paths are redesigned. |
| `folders.created_at` | Project Owner | Folder creation timestamp may continue to tolerate the current nullable database contract. | `APPROVED_KEEP_NULLABLE` | Revisit if lifecycle/audit requirements require strict timestamp presence. |
| `folders.updated_at` | Project Owner | Folder update timestamp may continue to tolerate the current nullable database contract. | `APPROVED_KEEP_NULLABLE` | Revisit if update lifecycle guarantees are formalized. |
| `notes.sort_order` | Project Owner | Note ordering may continue to tolerate the current nullable database contract. | `APPROVED_KEEP_NULLABLE` | Revisit if ordering semantics require strict non-null behavior. |

## Rationale

- Current schema allows `NULL`.
- No mandatory `NOT NULL` business constraint has been established.
- Avoiding unnecessary constraint migration reduces implementation and rollback risk.

## Boundary

This approval chooses the governance contract direction. It does not modify SQLAlchemy models, Alembic migrations, or the database. Any future metadata alignment must be separately designed, reviewed, and approved before implementation.

## Result

```text
Nullable Contract Status = APPROVED_KEEP_NULLABLE
```
