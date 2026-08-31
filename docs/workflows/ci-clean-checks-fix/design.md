# Design

## Verified Failure Boundaries

The PR merge workflow runs TypeScript before a Next build. `next-env.d.ts` is ignored, untracked, and generated locally; it currently supplies Next's `*.png` declarations. The three files in `src/components/liquid-grass/` are tracked, so the failure is a missing declaration in a clean checkout, not a missing asset.

The backend job starts a fresh PostgreSQL 16 service and then runs pytest directly. The job has no `alembic upgrade head` step, so the schema contains none of the tables required by database-backed tests.

## Chosen Changes

1. Add a tracked `*.png` declaration to `global.d.ts`, following the existing root declaration-file pattern. This makes TypeScript independent of ignored generated files.
2. Align the frontend CI runtime with `package.json` by selecting Node 24.
3. Add an Alembic migration step after dependency installation and before pytest. It must use the same disposable `DATABASE_URL` as pytest.

## Non-goals

- Do not change production database configuration or run migrations against any non-CI database.
- Do not alter application behavior, assets, package dependencies, deployment configuration, or Cloudflare settings.
- Do not treat existing AsyncMock warnings as part of this CI failure.
