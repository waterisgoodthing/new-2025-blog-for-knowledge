# Tasks

## Approval Gate

Implementation requires explicit approval of this task list.

- [x] Add a tracked PNG module declaration in `global.d.ts` and run the root TypeScript check.
- [x] Update `.github/workflows/ci.yml` to use Node 24 and initialize the disposable PostgreSQL schema with `alembic upgrade head` before pytest.
- [x] Validate the workflow structure and the updated local checks; record results in `validation.md`.
- [x] Commit, push, and verify the GitHub Actions rerun.
