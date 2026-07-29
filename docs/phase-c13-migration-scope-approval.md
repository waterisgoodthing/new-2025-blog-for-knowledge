# Phase C+13 Migration Scope Approval

Date: 2026-07-15
Status: governance scope approved; implementation not executed.

## Included Future Scope

Phase D may evaluate the following files and areas after separate execution approval:

```text
backend/main.py
backend/alembic/env.py
approved model metadata changes
approved migration files
```

Approved future objectives:

- remove production `create_all` dependency;
- add readiness validation;
- establish metadata authority;
- align approved metadata/index/nullable contract direction only within the authorized scope;
- preserve read-only readiness checks as separate from database mutation.

## Excluded Scope

The following remain excluded from the Phase D evaluation scope unless a separate governance review approves them:

```text
guest_messages
guest_message_bans

data cleanup

destructive migration

unapproved nullable changes

index deletion
```

## Explicit Prohibitions

This scope approval does not authorize:

- Python code changes in Phase C+13;
- SQLAlchemy model changes in Phase C+13;
- Alembic migration changes in Phase C+13;
- migration generation;
- `alembic upgrade`;
- `alembic downgrade`;
- DDL;
- DML;
- deployment.

## Result

```text
Migration Scope Status = APPROVED_FOR_PHASE_D_AUTHORIZATION_DRAFT
Implementation Status = NOT STARTED
```
