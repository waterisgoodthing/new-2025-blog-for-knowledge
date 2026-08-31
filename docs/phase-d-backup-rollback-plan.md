# Phase D Backup and Rollback Plan

Date: 2026-07-15
Status: plan template; no backup or restore executed.

## Backup

Backup must be completed and recorded before execution approval can become `APPROVED`.

| Item | Required value | Current status |
|---|---|---|
| Backup method | PostgreSQL logical backup or approved managed snapshot, plus any required attachment/storage metadata snapshot. | `PENDING` |
| Backup time | Exact timestamp of the execution-window backup. | `PENDING` |
| Backup location | Storage location or snapshot identifier with access instructions. | `PENDING` |
| Backup scope | Target database, Alembic revision metadata, schema, indexes, constraints, and migration-relevant rows. | `PENDING` |
| Restore verification | Isolated restore rehearsal with acceptance result. | `PENDING` |
| Evidence owner | Verification Owner. | Project Owner |

No `pg_dump`, managed snapshot, attachment copy, restore, or database command was executed in this phase.

## Rollback

Rollback must be approved before execution.

| Item | Required value | Current status |
|---|---|---|
| Rollback conditions | Backup unavailable, unexpected SQL, schema drift, validation failure, readiness failure, or operator stop decision. | Drafted |
| Rollback method | Restore from verified backup/snapshot or revert approved code/migration changes before database execution, depending on failure point. | `PENDING_VERIFICATION` |
| Rollback owner | Named rollback owner for the execution window. | `PENDING` |
| Rollback evidence | Restored revision, schema consistency, application startup, and post-rollback validation results. | `PENDING` |

## Required Before Approval

- Backup artifact or snapshot identifier.
- Backup timestamp.
- Restore rehearsal result.
- Rollback owner.
- Rollback procedure reviewed against exact migration SQL.
- Clear stop conditions accepted by the operator and verification owner.

## Current Status

```text
Backup Status = PENDING
Restore Verification = PENDING
Rollback Approval = PENDING
Execution Authorization = NOT APPROVED
```
