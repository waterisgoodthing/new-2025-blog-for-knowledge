# Migration Gate Closure Checklist

日期：2026-07-13  
当前结论：`Migration Gate = BLOCKED`

## Phase C+1 Evidence Update

| Evidence | Status | Finding |
|---|---|---|
| Schema entrypoints | PASS as audit / BLOCKED for closure | `Base.metadata.create_all` confirmed in application lifespan; Alembic online/offline paths confirmed; multiple schema authority remains |
| Alembic metadata coverage | BLOCKED | Runtime `Base.metadata`/target metadata observed with 37 tables, but coverage relies on package import side effect; migration history has 35 create-table records and no create record found for `guest_messages` / `guest_message_bans` |
| Three-way drift | BLOCKED | Four nullable differences and `idx_notes_folder_id` drift reproduced; all remain `unknown` pending approved classification |
| Schema authority decision | DESIGNED, not implemented | Alembic-only target documented; no `create_all` or migration path changed |
| Schema authority validation | PASS as read-only evidence | Commands and no-write boundary recorded in `schema-authority-validation.md` |

This update adds evidence only. It does not change any `BLOCKED` item to `READY`.

## Phase C+2 Evidence Update

| Evidence | Status | Finding |
|---|---|---|
| Migration provenance inventory | PASS as inventory / BLOCKED for closure | 35 application tables have migration create records; `guest_messages` and `guest_message_bans` have none |
| Guest table origin | BLOCKED | Active model/router/docs evidence exists; current physical origin remains `UNKNOWN`; dev `create_all` is documented as a candidate only |
| Complete coverage matrix | BLOCKED | Two tables are `MIGRATION_MISSING`; no model-only table observed; `alembic_version` is expected bookkeeping |
| Column drift ownership | BLOCKED | Four fields have zero current NULL rows, but ownership remains `unknown` |
| Index drift ownership | BLOCKED | `idx_notes_folder_id` is DB-present, model-absent, migration-005-created; final ownership remains `unknown` |
| Provenance validation | PASS as read-only evidence | No migration/DDL/DML/code/config change executed |

This update records evidence only. Migration Gate remains `BLOCKED`.

| Item | Status | Evidence Required |
|---|---|---|
| Schema authority | BLOCKED | Alembic-only target decision implemented in an approved later change; `create_all` production path removed/disabled; complete metadata import coverage; database/model/migration three-way drift report; clean `alembic check` |
| Owner contract | BLOCKED | explicit/inferred/unknown contract approved; per-row `owner_mapping` dry-run with stable key/content hash/relation hash; all conflicts reviewed; no default admin/created_by/session/worker owner inference |
| Backup restore | BLOCKED | fresh PostgreSQL backup evidence; isolated restore rehearsal; schema/revision, table/row counts, PK ranges, FK/polymorphic integrity; attachment metadata/blob checksum, size and storage-key validation; smoke evidence |
| Permission test | BLOCKED | public/authenticated/admin/worker integration tests for all six objects; own vs other owner; target mismatch; AI replay; sensitive-field redaction; AUTH_BYPASS four-state results |

## Additional closure items

| Item | Status | Evidence Required |
|---|---|---|
| AI audit correlation | BLOCKED | `ai_runs` to `ai_call_logs` relationship either proven and owner-scoped, or explicitly classified as audit-only with no unsafe owner mapping |
| Attachment recovery | BLOCKED | same-snapshot metadata/blob inventory and per-object checksum report |
| Compatibility window | BLOCKED | old/new read/write ownership, stop condition, cutover, rollback and approval record |
| Validation record | BLOCKED | dated machine-backed validation file with exact commands, results, failures and no-write proof |

## Phase D entry conditions

Phase D is allowed only after all of the following are true:

1. Every P0/P1 item above is `PASS`, with evidence linked from the task workspace.
2. All UNKNOWN classifications affecting schema, owner, backup, attachment or authorization are resolved or explicitly rejected by the migration owner; unresolved unknowns remain a stop condition.
3. `alembic check` is clean after an approved schema-authority convergence change; no new migration is created merely to silence unexplained drift.
4. Owner mapping is approved row-by-row or the migration scope explicitly excludes unresolved rows with a reviewed disposition; no implicit owner assignment is used.
5. Restore rehearsal and attachment validation pass in isolation, and business smoke tests pass.
6. Permission integration tests pass without `AUTH_BYPASS`; the double-true bypass combination is not accepted as production readiness.
7. A separate human approval explicitly authorizes Phase D execution, including any migration/upgrade, data write, permission change, cutover or rollback action.

Until then, the following remain prohibited: migration creation/execution, upgrade/downgrade, pg_dump/pg_restore, database or owner writes, permission/config changes, old-table deletion, cutover and production data modification.

## Final decision

```text
Phase C+ Design Completed

Migration Gate:
BLOCKED

Next Approval Required:
Human approval before execution phase
```
