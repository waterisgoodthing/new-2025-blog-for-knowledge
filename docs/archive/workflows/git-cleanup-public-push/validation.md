# Validation — Git Cleanup And Public Push

Current status: `2026-07-29 release completed and publicly verified`

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

---

## 2026-07-29 Release Run

Status: `VALIDATION PASSED — proceeding to scoped Git publication`

### Preflight

- Upstream fetch: PASS.
- Branch divergence after fetch: local 3 ahead, 0 behind.
- Dirty-surface snapshot: 12 tracked modifications and 334 untracked files
  before adding this release-run's workflow records.
- Public-safety classification: 331 publish, 14 exclude, 1 publish after
  relocation, 0 awaiting user decision.
- Private authenticated UI evidence is preserved locally and ignored by the exact
  rule `/docs/ui-review/artifacts/authenticated/`.
- Duplicated C6-C12 review report was moved to
  `docs/workflows/i-series-completion-plan/C6-C12-REVIEW-REPORT.md`.
- No file was deleted, reset, checked out, or discarded.

### Validation

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| Untracked Markdown relative links | PASS after correcting 4 stale `dashboard-*` asset links to the existing `dashboard-preferences-*` files |
| Untracked JSON parse | PASS, 15/15 files |
| Initial isolated `npm run predeploy:check` | BLOCKED: production audit had 10 high and 0 critical vulnerabilities |
| Remediated isolated `npm run predeploy:check` | PASS: audit 0 vulnerabilities; frontend 58/58; backend 300/300; TypeScript, Cloudflare build, Alembic 025 and schema check passed |

The link/JSON checker covered 120 Markdown files and 15 JSON files. Its first run
found four missing image targets in
`docs/workflows/i4-i5-closure-fix-2/validation.md`; the links were corrected and
the full check then passed.

### Fail-Closed Release Blocker

The exact candidate application commit was checked from a detached worktree at
`beb7897`. Two fresh local validation databases were created; the target was
upgraded through Alembic `024 (head)`. The first predeploy invocation rejected
the local `.venv` dependency symlink as dirty; a command-scoped Git exclude was
then used so the repository itself remained unchanged. The second invocation
reached the live production audit and stopped.

Audit summary:

- high: 10
- critical: 0
- direct high packages: `next@16.2.10`,
  `@opennextjs/cloudflare@1.20.1`
- additional affected transitive packages:
  `@node-minify/core`, `@opennextjs/aws`, `brace-expansion`, `glob`,
  `linkify-it`, `minimatch`, `postcss`, and `sharp`
- npm reports `next@16.2.12` as an available non-major fix path for the
  Next/PostCSS/Sharp group
- npm's suggested OpenNext fix is `@opennextjs/cloudflare@0.2.1`, a major
  downgrade from the installed `1.20.1`; it must not be applied automatically

Release decision:

- do not stage
- do not commit
- do not push
- do not deploy
- require a separately approved dependency-runtime remediation task, followed
  by a fresh exact-commit predeploy gate

### Validation Cleanup

- Temporary test database `gcp_r2_test_20260729185159`: removed.
- Temporary target database `gcp_r2_target_20260729185159`: removed.
- Detached validation worktree: removed.
- Remaining temporary release directory, containing only the audit JSON and
  command-scoped exclude file: moved to
  `/Users/limengyang/.Trash/git-release-gate.V93yoY` and remains recoverable.
- Source database `blog_db`: not modified.
- Final branch divergence: local 3 ahead, 0 behind.
- Final `git diff --check`: PASS.

---

## 2026-07-29 Remediation And Public Closure

The dependency-runtime remediation workflow resolved the earlier audit blocker.
The exact release candidate passed:

- dependency audit: 0 vulnerabilities;
- frontend: 58/58;
- backend: 300/300;
- TypeScript and 40-route Cloudflare/OpenNext build;
- Alembic `025 (head)` and `No new upgrade operations detected`.

Git publication:

- branch: `notes-workspace-ux-upgrade`;
- pushed commit: `c12af9a056e1ed58a5364e00392920fde63e785d`;
- remote: `mine`;
- force push: not used;
- post-push equality: local HEAD and remote branch matched.

The public deployment ran from a detached worktree at that exact commit using
`NEXT_PUBLIC_API_URL=https://public-api.limengyang.me npm run deploy:full`.
Its fail-closed frontend gate passed before Wrangler uploaded the Worker.

Deployment evidence:

- Worker: `2025-blog-public`;
- route: `blog.limengyang.me/*`;
- Worker Version ID: `23e67efe-d042-435b-a6b7-4236839a8477`;
- Build ID: `RHki-tQ1KONo-bfoHR6ng`;
- public `/BUILD_ID`: exact match.

Public HTTP verification:

| Boundary | Result |
| --- | --- |
| `/` | 200 HTML |
| `/blog` | 200 HTML |
| `/notes` | 200 HTML |
| `/mistakes` | 200 HTML |
| `/manage` | 200 HTML; page remains the login/management boundary |
| API `/api/health` | 200 JSON, `{"status":"ok"}` |
| API `/api/admin/profile` without credentials | 401 JSON, `Not authenticated` |

The 14 authenticated/private UI evidence files remain local and excluded by the
exact `.gitignore` rule. They were not published or deleted.
