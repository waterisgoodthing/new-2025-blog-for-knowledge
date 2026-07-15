# Phase D-1 Code Change Draft Review

Date: 2026-07-15
Mode: code-change draft review; no code modified.

## `backend/main.py`

Current finding:

- `Base.metadata.create_all` is called in application lifespan:

```text
await conn.run_sync(Base.metadata.create_all)
```

Draft change needed:

- Remove the production startup schema mutation path.
- Replace it with read-only readiness validation.
- Keep `/api/health` database connectivity behavior or add a separate readiness route/check that does not create, alter, or migrate schema.
- Do not run Alembic from application startup.

Risk:

- Local or dev environments that currently rely on startup auto-create may fail until they run explicit Alembic setup.
- The readiness check must fail clearly without mutating schema.

## `backend/alembic/env.py`

Current finding:

- `target_metadata` currently comes from `Base.metadata`.
- Several model modules are explicitly imported.
- The import coverage is not represented as a deterministic registry with an auditable coverage list.

Draft change needed:

- Establish a deterministic metadata authority.
- Use explicit model imports or a single explicit registry module.
- Keep `target_metadata = Base.metadata` only after deterministic imports have populated it.
- Add/maintain a documented coverage list for included and intentionally excluded model modules.
- Avoid router/service imports and implicit package scanning.

Risk:

- Missing model import could hide metadata from autogenerate.
- Including excluded guest schema would violate Phase C+13 scope.
- Reordering imports carelessly could affect metadata registration.

## `backend/app/models/note.py`

Current finding:

- `idx_notes_folder_id` exists in migration `005_add_folders.py`.
- `Note.folder_id` exists in the model.
- `Note.__table_args__` does not currently include `Index("idx_notes_folder_id", "folder_id")`.

Draft change needed:

- Add ORM metadata alignment for the existing database/migration index only:

```python
Index("idx_notes_folder_id", "folder_id")
```

Risk:

- If a target database lacks the physical index, autogenerate may propose creating it. That must stop for review.
- Do not delete, rename, recreate, or change the index.
- Do not change nullable fields.

## Summary Table

| File | Change Needed | Risk |
|---|---|---|
| `backend/main.py` | Remove production `Base.metadata.create_all` startup mutation; add read-only readiness validation. | Dev/local startup may reveal missing explicit migration setup; readiness must not mutate schema. |
| `backend/alembic/env.py` | Establish deterministic metadata authority and auditable model import coverage. | Missing imports hide metadata; accidental guest inclusion violates scope. |
| `backend/app/models/note.py` | Add `idx_notes_folder_id` ORM metadata alignment only. | Autogenerate must be reviewed to avoid unintended create/drop operations. |

## Status

```text
Code Change Draft Review = COMPLETE
Code Modification = NONE
```
