# W3-00 Rework Report (agent: W3-00-rework)

Scope: W3R-01..W3R-04 only. W3R-05 deferred to PR-11. No `backend/app/**`,
`backend/alembic/**`, `src/**`, no git writes, no DB connections.

## Changes

### W3R-01 BLOCKER — dual-arg bypass (FIXED)
`scripts/week3-scratch-guard.py`:
- `validate_target` now derives the effective database name from the **connection
  URL** whenever a URL is the string that will actually be used (`--url`, or
  `env:DATABASE_URL`). `--db-name` is only authoritative when no URL is supplied.
- When both `--db-name` and `--url` are given and the parsed names disagree →
  `GuardError` ("ambiguous target") → exit 1, child never runs.
- Allowlist `^astra_week3_[a-z0-9_]+$` is applied to the URL-derived name, so
  `--url .../production_db` (or `blog_db` / `blog_v2`) FAILs even when
  `--db-name` is legal.
- `run` injects `DATABASE_URL` = the validated URL/DSN and nothing else.

### W3R-02 MEDIUM — host allowlist (FIXED, fail-closed)
- `ALLOWED_HOSTS = {localhost, 127.0.0.1, ::1}`; any other host (or an
  unresolvable hostname) → `GuardError` unless `--allow-remote-host` is passed.
- With `--allow-remote-host` a `WARNING: ...` line is printed to **stderr**.
- Flag added to both `check` and `run` subcommands.

### W3R-03 LOW — `hidden is False` identity comparison (FIXED)
`backend/tests/week3_contracts_support.py` `map_legacy_note_to_mistake_visibility`:
- `is_public = status == published and not bool(hidden)`.
- Truthy `hidden` (True/1/...) → private; falsy (False/0/None) → visible when
  published. Unpublished remains private regardless.

### W3R-04 LOW — ratio bounds (FIXED)
`compute_attempt_rates`:
- `graded_attempts < 0` → `ValueError`.
- `not (0 <= wrong_count <= graded_attempts)` → `ValueError`.
- `graded_attempts == 0` (and `wrong_count == 0`) still returns `(0.0, 0.0)`.

## Evidence

Commands and outputs in `evidence/tests/`:
- `w3-00-rework-guard-tests.txt` — 36 tests, `OK` (includes new dual-arg and
  host-allowlist negatives).
- `w3-00-rework-contracts-pytest.txt` — 51 tests, `51 passed`.
- `w3-00-rework-repro.txt` — A/B/D reproductions:
  - A (dual-arg mismatch) → `FAIL: ambiguous target` exit 1.
  - B (`--url production_db` + legal `--db-name`) → FAIL exit 1.
  - B2/B3 (`--url blog_db` / `blog_v2` + legal `--db-name`) → FAIL exit 1.
  - D (run, dual mismatch) → `child command NOT executed` exit 1.
  - D2 (run, consistent dual args) → `CHILD_DSN postgresql+asyncpg://.../astra_week3_other` exit 0.
  - Remote host without flag → FAIL; with flag → PASS + stderr `WARNING`.

## Verification

| Check | Result |
|---|---|
| `python3 scripts/week3-scratch-guard.test.py -v` | PASS — 36 tests OK |
| `cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q` | PASS — 51 passed |
| A reproduction | PASS (FAIL as required) |
| B reproduction | PASS (FAIL as required) |
| D reproduction | PASS (child not executed / CHILD_DSN legal) |
| `git status --short` — write-scope check | PASS — only the 4 allowed source files + this report + `evidence/tests/w3-00-rework-*.txt` touched by this rework |

## Risks

None beyond the intended tightening: `--allow-remote-host` is the only escape
hatch for non-local hosts and is explicit + loud. `compute_attempt_rates` now
raises on previously silent out-of-range inputs (callers in tests only).

## Remaining

- W3R-05 (dashboard/empty_metadata completeness) intentionally untouched — owned
  by PR-11.

## Decision Needed

None.

**Self-assessment: ACCEPT**
