# Phase C+6 Approval Checklist

Date: 2026-07-14
Status: all approvals pending; `Migration Gate = BLOCKED`.

## Governance Approval

- [ ] Schema owner approval
- [ ] Guest ownership approval
- [ ] Nullable contract approval
- [ ] Index policy approval
- [ ] Explicit approval of the Alembic-only authority transition

## Database Safety

- [ ] Backup exists
- [ ] Restore tested
- [ ] Rollback plan reviewed
- [ ] Existing data compatibility reviewed
- [ ] No destructive operation is included without separate approval

## Migration Review

- [ ] SQL reviewed
- [ ] Operation order reviewed
- [ ] Affected objects confirmed
- [ ] Guest migration baseline approved, if guest tables are in scope
- [ ] Nullable target semantics approved, if columns are in scope
- [ ] Index policy and autogenerate impact reviewed

## Deployment

- [ ] Operator assigned
- [ ] Deployment window assigned
- [ ] Monitoring available
- [ ] Failure escalation defined
- [ ] Readiness and smoke verification owner assigned
- [ ] Post-change evidence capture defined

## Gate rule

Any unchecked item is a blocker. No approval checklist item is considered complete from repository intent alone. Until every required item is approved and evidenced, Migration Gate remains `BLOCKED`.
