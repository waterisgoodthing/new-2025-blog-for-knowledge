# Validation Plan

## Route And Permission

- Enumerate built routes and verify public routes remain reachable without admin session.
- Verify private pages use `AuthGate` and protected backend mutations retain `get_current_admin`.
- Verify anonymous public rendering does not request review, AI, upload, capture, or management APIs.

## Compatibility

- Exercise or inspect old `/write-*`, public detail, and `/manage/**` links.
- Record preserve/redirect/notice decisions before changing routes.
- Check missing resources and dangerous actions have recovery/confirmation states.

## Regression

- Frontend tests, TypeScript, production build.
- Targeted backend route/auth tests.
- `PYTHONPATH=. .venv/bin/alembic current` and, if appropriate, `alembic check` with known drift separated.
- Read-only counts/IDs for all Batch 2-5 data-bearing tables.

## Closure

No Batch 7 acceptance until all evidence is recorded. Do not begin another batch automatically.
