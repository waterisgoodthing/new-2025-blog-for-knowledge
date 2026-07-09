# Validation — Git Cleanup And Public Push

Status: `completed with deployment blocked`

Validation date: 2026-07-09.

## Initial Preflight Snapshot

- Branch: `notes-workspace-ux-upgrade`
- Remote: `mine` -> `https://github.com/waterisgoodthing/new-2025-blog-for-knowledge.git`
- Current deployment concern: `package.json` does not expose `deploy` / `build:cf`; `wrangler.toml` and `open-next.config.ts` are currently deleted in the working tree.

## Local Validation

| Check | Command | Result |
| --- | --- | --- |
| Backend pytest | `cd backend && .venv/bin/python -m pytest tests/ -ra` | Passed: `226 passed, 2 warnings in 4.13s`. |
| Alembic current | `cd backend && PYTHONPATH=. .venv/bin/alembic current` | Passed: `018 (head)`. |
| TypeScript | `npx tsc --noEmit` | Passed. |
| Frontend build | `npm run build` | Passed. Next.js generated 37 app routes. Existing warnings: stale `baseline-browser-mapping` data and Node `DEP0205 module.register()` deprecation. |
| Setup check | `npm run check` | Passed with warnings: Python 3.14 unsupported warning with Python 3.12 selected; Docker missing; root `.env` missing; ports 2025/8000 in use. |
| Diff whitespace | `git diff --check` | Passed. |

Pytest warnings:

- `backend/tests/test_ai_gateway.py::LogWriteFailureTest::test_log_write_failure_does_not_block`
- `backend/tests/test_ai_gateway.py::LogWriteFailureTest::test_write_call_log_catches_exception`

Both are the known `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited` warnings in `backend/app/services/ai_gateway.py:98`.

## Staging Review

Staging command:

```bash
git add -A
```

Staged scope:

- 251 files staged.
- Staged stat: `34052 insertions(+), 12867 deletions(-)`.

Secret/cache scan:

```bash
git diff --cached --name-only | rg '(^|/)(\.env$|\.env\.local|\.env\.production|.*\.pem$|.*\.key$|.*\.p12$|.*\.sqlite$|.*\.db$|.*dump.*|node_modules/|\.next/|\.open-next/|\.output/|backend/\.venv/|__pycache__/|\.pytest_cache/)'
```

Result: no matches.

Allowed template note:

- `.env.example` is staged as a template file, not a real secret file.

## Deployment Preflight

Deployment is blocked in the current update set.

Evidence:

- `package.json` no longer contains `deploy`, `deploy:full`, `build:cf`, or `preview` scripts.
- `package-lock.json` no longer contains the old OpenNext/Wrangler dependency set.
- `wrangler.toml` is staged for deletion.
- `open-next.config.ts` is staged for deletion.

Conclusion:

- Git commit and push can proceed after validation.
- Public Cloudflare deployment cannot proceed from this committed tree without restoring or replacing the deployment configuration in a separately approved repair task.
- This workflow will not invent a new deployment path.

## Git Commit And Push

Release commit:

```text
2b5453f feat: finalize AI learning system acceptance
```

Push result:

```text
To https://github.com/waterisgoodthing/new-2025-blog-for-knowledge.git
   1cb7c7a..2b5453f  notes-workspace-ux-upgrade -> notes-workspace-ux-upgrade
```

Follow-up status-record commit:

```text
71d958b docs: record public deployment blocker
```

## Public Deployment Result

No public deployment was run.

Reason:

- The pushed commit does not contain the previously documented Cloudflare/OpenNext deployment path.
- `wrangler.toml` and `open-next.config.ts` are deleted.
- The package scripts and dependencies required for the old deployment path are removed.

Decision:

- Stop at the approved safety boundary.
- Do not recreate deployment config or invent a new deployment architecture in this workflow.
- A new deployment-repair task is required before pushing the current frontend to `blog.limengyang.me`.
