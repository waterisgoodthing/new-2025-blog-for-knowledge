# Migration Execution Plan

Date: 2026-07-14  
Phase: C+5 planning only  
Execution status: not executed.

## Preconditions

No migration may begin until all of the following are explicitly approved and evidenced:

- Backup is available for the target database and relevant data.
- Restore procedure has been tested or otherwise accepted with evidence.
- Migration design and generated SQL have been reviewed by the schema owner and operator.
- Owner approval exists for guest ownership, nullable semantics, index policy, and authority transition.
- Data impact review covers existing guest rows, potential NULL rows, defaults, constraints, and index behavior.
- Rollback strategy is documented and operationally feasible.
- Verification plan and acceptance criteria are agreed before the change window.
- A controlled deployment window, operator, observability, and failure escalation path are assigned.

## Migration Order

The future implementation sequence is:

1. Remove production startup `create_all` from the application schema-provisioning path.
2. Introduce and validate the explicit metadata registry and deterministic Alembic target metadata coverage.
3. Add readiness behavior that checks connectivity, supported Alembic revision, and schema compatibility without writing schema.
4. Generate and review only the specifically approved migration remediation.
5. Apply the approved migration in the controlled deployment window.
6. Run verification and record results before declaring the release ready.

The guest migration, nullable changes, or index changes must not be inserted into step 4 unless their separate approvals are complete. If an item remains `UNKNOWN`, it stays out of the migration.

## Rollback Strategy

### Migration rollback

Use a reviewed Alembic downgrade only when the migration is explicitly reversible, the downgrade has been reviewed, and data loss/constraint effects are understood. A downgrade is not an automatic response to every failure.

### Restore path

If downgrade is unsafe, incomplete, or destructive, stop application rollout and restore the approved backup to a controlled recovery target. Reconcile the restored revision and schema metadata before resuming service.

### Failure handling

- Stop at the first failed precondition or verification check.
- Do not retry a failed DDL operation blindly.
- Preserve logs, applied revision, database snapshot identifiers, and operator actions.
- Keep the application not-ready if schema compatibility is uncertain.
- Escalate any data mismatch, lock timeout, partial migration, or unexpected object change to the schema owner and operator.

## Verification Checklist

- Run `PYTHONPATH=. .venv/bin/alembic current` from `backend/` and record the revision.
- Run `PYTHONPATH=. .venv/bin/alembic check` and confirm the approved target produces no unreviewed operations.
- Compare database schema metadata with approved model and migration expectations: tables, columns, nullability, defaults, constraints, foreign keys, and indexes.
- Verify the explicit metadata registry and Alembic target coverage.
- Verify startup readiness and liveness behavior.
- Run application smoke tests for health, folder/note access, and any approved guest behavior.
- Confirm no unapproved table, column, nullable, constraint, or index changes occurred.
- Record backup/restore evidence, logs, revision, verification results, and final approval decision.

This plan is a future execution design. No migration, downgrade, DDL, DML, or schema change is executed in Phase C+5.
