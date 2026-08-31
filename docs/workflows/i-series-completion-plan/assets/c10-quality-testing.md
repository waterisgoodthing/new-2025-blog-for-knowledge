# C10 Quality Testing

Date: 2026-07-29

## Final Results

| Gate | Final result |
|---|---|
| `npm test` | PASS: 21 files, 58/58 tests |
| `npx tsc --noEmit` | PASS |
| `npm run build` | PASS: compiled, TypeScript checked, 40/40 static pages generated |
| `python3 -m compileall -q backend` | PASS |
| Backend `.venv/bin/pytest -q` | PASS: 300/300 tests |
| C6/C1 Python unit tests | PASS: 5/5 tests plus `py_compile` |
| Alembic current/heads/check | PASS: current=`024 (head)`, heads=`024 (head)`, `No new upgrade operations detected` |
| `git diff --check` | PASS |

The frontend suite still emits React `act()` warnings for asynchronous AI-runs panel state, and the backend suite emits two existing `AsyncMock` coroutine warnings in `test_ai_gateway.py`. They did not fail tests, but remain test-hygiene follow-ups.

## Diagnosed Failures

The first backend full-suite run was 296/300. All four failing cases passed in fresh processes, proving fixture/process contamination rather than runtime behavior regressions. Two test-only fixes were then applied:

1. `test_registry_does_not_import_business_services` now restores the `sys.modules` entries it temporarily removes. The former global mutation made later string-based patches target a re-imported module while collected tests retained stale function objects.
2. `MistakeReviewServiceTest.asyncSetUp` discards a prior loop's asyncpg pool before creating a session for a new `IsolatedAsyncioTestCase` loop.

After these fixes, the complete backend suite passed 300/300 in one process with `AUTH_BYPASS=false`, empty AI provider keys, and the isolated acceptance database.

One Alembic command attempt applied `PYTHONPATH=.` only to the first command in a chain, causing the later `alembic check` process to fail importing `app`. Exporting the environment for the shell and rerunning produced a clean PASS. No schema change occurred.

Conclusion: `PASS`.
