# Alembic-only Transition Plan

Status: design only; no implementation authorized in C+3.

## Target authority

```text
Alembic migration
        |
        v
Database schema
```

`Base.metadata` remains the declarative comparison source for Alembic, but application startup must not be a competing provisioning authority.

## Application startup

Current behavior is `backend/main.py:41-42`:

```text
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

Future design: replace schema provisioning with read-only revision/readiness/health checks. Startup may verify database connectivity, expected Alembic revision, and application readiness. It must fail clearly when the schema is not ready rather than creating or altering objects.

## Development and test environment

- Use an isolated test database for each test run or controlled fixture lifecycle.
- Provision that database through an explicit Alembic command or an approved fixture setup, never by relying on production startup behavior.
- Keep test fixtures and seed data separate from migration files.
- Treat `alembic check` and metadata inspection as comparison evidence, not as a migration execution substitute.
- Do not use local auto-create behavior as a proxy for production readiness.

## Production deployment

The controlled sequence is:

```text
backup
  -> migration approval
  -> upgrade
  -> verification
```

Verification must include applied revision, schema metadata, application readiness, critical read/write smoke checks, and rollback/restore evidence as appropriate. Application startup must never automatically modify production schema.

## Transition prerequisites

1. Resolve guest-table provenance and choose official retention or deprecation.
2. Resolve the four nullable semantics and the index metadata policy.
3. Design and approve any required Alembic remediation separately.
4. Remove `create_all` from the production application lifecycle in an approved implementation phase.
5. Add readiness behavior that checks revision/schema compatibility.
6. Validate isolated development/test provisioning and production deployment rehearsal.

Until these prerequisites are approved and implemented, the current architecture remains multiple-authority and the Migration Gate is `BLOCKED`.
