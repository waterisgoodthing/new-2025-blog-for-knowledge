# Schema Provenance Validation

日期：2026-07-14  
状态：Phase C+2 audit complete; `Migration Gate = BLOCKED`。

## Executed

### Repository search

```text
rg -n -i 'guest_messages|guest_message_bans|GuestMessage|GuestMessageBan' backend alembic scripts deployment docs
rg --files backend/alembic/versions
```

Search covered model, router, schema, application registration, migration, scripts/deployment paths and prior workflow docs.

### Migration inspection

- Static AST/text inventory of all `backend/alembic/versions/*.py` files.
- `PYTHONPATH=. .venv/bin/alembic current`
- `PYTHONPATH=. .venv/bin/alembic history --verbose`
- `PYTHONPATH=. .venv/bin/alembic check`

Results: current `018 (head)`; single chain; `alembic check` still fails on the four nullable differences and `idx_notes_folder_id`.

### Metadata/database SELECT inspection

- `Base.metadata` table inventory in a clean Python process.
- `information_schema.columns` for guest tables and drift columns.
- NULL counts for all four drift columns.
- `pg_indexes` for guest tables and `idx_notes_folder_id`.
- `pg_constraint`/`pg_tables` coverage checks.

Observed NULL counts: `folders.sort_order 0/2`, `folders.created_at 0/2`, `folders.updated_at 0/2`, `notes.sort_order 0/13`.

## Not Executed

```text
No migration executed.
No schema modified.
No database write executed.
No CREATE/ALTER/DROP executed.
No upgrade/downgrade executed.
No migration created.
No table or index deleted.
No backend/model/Alembic/config/auth/deployment file modified.
```

## Validation Outcome

| Area | Result | Closure state |
|---|---|---|
| migration provenance inventory | PASS as inventory | guest tables still UNKNOWN |
| guest table origin | PASS as investigation | current physical origin UNKNOWN; dev `create_all` is only documented candidate |
| complete coverage matrix | BLOCKED | two `MIGRATION_MISSING` tables |
| column drift ownership | BLOCKED | four fields remain `unknown` |
| index drift | BLOCKED | observed three-way difference remains `unknown` ownership |
| write boundary | PASS | read-only commands/SELECT only |
| Migration Gate | BLOCKED | no P0 schema authority closure |

