# Validation

## Baseline

- GitHub Actions run `30696127193` failed on 2026-08-01.
- Frontend: TypeScript could not resolve three PNG imports because ignored `next-env.d.ts` is absent from the clean checkout.
- Backend: `68 failed, 239 passed`; the first failures are missing `users`, `subjects`, `attachments`, and `alembic_version` relations in the uninitialized CI database.
- Local baseline: `npx tsc --noEmit` passes because generated `next-env.d.ts` exists locally; `backend/.venv/bin/python -m pytest tests/ -q` passes with `307 passed, 2 warnings` against the local migrated database.

## Task 1: Tracked PNG Types

- Added `declare module '*.png'` to `global.d.ts`, returning `import('next/image').StaticImageData`.
- Simulated a clean checkout by temporarily moving ignored `next-env.d.ts` out of the repository before running `npx tsc --noEmit --pretty false`; the command passed and the generated file was restored.

## Task 2: CI Runtime and Schema Initialization

- Updated the frontend job to use Node 24, which matches `package.json` engines.
- Moved the backend job's disposable database settings to job scope and added `python -m alembic upgrade head` before pytest.
- Ruby YAML parsing and a CI contract check confirmed Node 24, the migration-before-test order, and the test database URL.
- Local Alembic metadata checks passed: `heads=025`, `current=025`, and `check=No new upgrade operations detected`.

## Task 3: Final Local Validation

- `npm test`: 23 test files and 64 tests passed.
- `npx tsc --noEmit --pretty false`: passed.
- `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8000 npm run build`: passed; 40 static pages generated.
- `backend/.venv/bin/python -m pytest tests/ -q --tb=short`: 307 passed. Two pre-existing AsyncMock RuntimeWarnings remain and are outside this CI initialization repair.
- `.github/workflows/ci.yml` parses as YAML and the CI contract check passed.
- `git diff --check`: passed.

## Remaining External Verification

- The CI workflow must be committed and pushed before GitHub Actions can validate the disposable-PostgreSQL path on a clean runner.
