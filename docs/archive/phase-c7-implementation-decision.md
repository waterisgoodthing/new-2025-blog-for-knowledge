# Phase C+7 Implementation Authorization Decision

Date: 2026-07-14
Decision: `BLOCKED`
Authorization status: `NOT APPROVED`.

## Blockers

- Missing mandatory project context documents: `docs/README.md`, `docs/requirements.md`, and `docs/design.md`.
- Guest schema owner and physical provenance remain `UNKNOWN`.
- Guest migration ownership and existing data compatibility are not approved.
- Nullable business contracts and owners are not approved for four fields.
- `idx_notes_folder_id` metadata policy is not approved.
- Backup availability and restore testing are not evidenced as complete.
- Rollback, migration SQL review, operation ordering, verification, operator, deployment window, monitoring, and escalation approvals are incomplete.
- Production `create_all` removal, readiness check, and explicit metadata registry remain unimplemented.

## Required evidence

1. Complete or formally waive the missing project context through an approved governance decision; do not silently substitute documents.
2. Name schema, release, and verification owners.
3. Close guest provenance/ownership or explicitly exclude guest tables from the approved migration scope.
4. Approve nullable contracts using business and historical/write-path evidence, not NULL count alone.
5. Approve the index policy and its model/Alembic implications.
6. Produce backup/restore, rollback, SQL review, verification, deployment, and escalation evidence.
7. Record exact authorized files and exact migration objects in a signed authorization record.

## Next approval condition

Phase D may be reconsidered only when all required evidence exists, all P0 `UNKNOWN` items are resolved or explicitly excluded, the C+6 checklist is complete, and a named approver authorizes the exact implementation scope.

No files are authorized by this document. No migration, DDL, DML, code change, model change, or database operation is permitted in Phase C+7.
