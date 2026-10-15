# Temporary Admin Bootstrap Tasks

Implementation has not started. Explicit approval of this task list is required before code changes.

- [x] Add focused test coverage for the temp-admin bootstrap behavior, or document why the local DB dependency makes targeted testing impractical.
  - Evidence: Added `backend/tests/test_temp_admin_bootstrap.py`; red run fails because `bootstrap_temp_admin` is not implemented yet.
- [x] Update `backend/app/cli.py` with a `create-temp-admin` command that creates or rotates a temporary admin user using existing hashing and DB patterns.
  - Evidence: Added `create-temp-admin` CLI command, default `temp-admin` username, generated one-time password output, and `bootstrap_temp_admin()` helper. Focused test passes.
- [x] Add a safe cleanup or rotation path in docs or CLI help so the temporary account is not treated as permanent.
  - Evidence: Added `disable-temp-admin` CLI command and documented cleanup usage in `design.md`; focused test verifies the account loses admin privileges and receives a disabled password sentinel.
- [x] Run backend validation appropriate to the touched code.
  - Evidence: `cd backend && .venv/bin/python -m pytest tests/test_temp_admin_bootstrap.py` passed; `python -m app.cli --help` showed both temp-admin commands; `py_compile` passed.
- [x] Record validation results in `validation.md`.
  - Evidence: Validation file updated with commands, results, and account creation outcome.

## Approval Gate

Pending user approval. Do not implement these tasks until the user explicitly approves this `tasks.md` list.
