# PR-17 / F04 — Restored R22b business E2E (E2E-03, E2E-04)

**Status:** locally verified PASS (scratch stack, same-site, no `/etc/hosts` edit).
Remote GitHub Actions: **NOT_VERIFIED** (push not authorized).

## Conclusion

The two placeholder specs that only asserted capture-mode tabs / the review empty-state are
replaced with real R22b business flows that perform page operations and assert the persisted
outcome by reading the backend API:

| Spec | Requirement | Real flow exercised | Backend readback asserted |
|---|---|---|---|
| `tests/e2e/03-capture.spec.ts` | E2E-03 question → wrong attempt → mistake draft | `/manage/questions/<id>` → 作答验证 → submit wrong answer → UI navigates to `/manage/mistakes/<draft>?kind=draft` | `POST /api/admin/attempts` response + `GET /api/admin/mistake-drafts` finds the draft by `draft_item_id`, with `attempt_id`, `question_id`, `status='pending'`, `question_text`, `my_answer` |
| `tests/e2e/04-review-flow.spec.ts` | E2E-04 mistake → review → re-answer → review record | `/manage/review` due card → 再答 → submit answer → click recommended rating 4 → success banner | `POST /api/admin/attempts/review` + `POST /api/admin/review/items/<id>/submit` responses + `GET /api/admin/review/items/<id>/records` newest record has `rating=4` and `attempt_id` equal to the re-answer attempt id |

E2E-01/02/05 are unchanged and still pass.

## Deterministic seed

`tests/e2e/seed/seed_week4_business.py` (run by `tests/e2e/global-setup.ts` before the suite, under
`backend/.venv` with `PYTHONPATH=backend`):

- refuses any target that is not a local `astra_week4_*`/`astra_week3_*` DB (`require_scratch_database`);
- bootstraps/rotates admin `ci-admin` / `ci-test-admin-password` via `app.cli.bootstrap_temp_admin`;
- find-or-creates Subject `E2E 业务闭环`, KnowledgePoint `E2E-04 复习知识点`;
- find-or-creates active `short_answer` Question title `E2E-W4-BUSINESS-Q`, question_text
  `E2E-W4-REVIEW-Q 固定间隔复习 v2：连续成功第 1 次应推进到几天？`, `answer_data.value="3"`,
  linked to the KP via `question_knowledge_points`;
- find-or-creates a converted Mistake (by reusing an existing converted mistake draft, else through
  the real `mistake_service.create_mistake_draft` + `convert_mistake_draft`) and **resets its
  ReviewItem to due** (`state=active`, `next_review_at=now`, `repetitions=0`, `interval_days=0`,
  `last_reviewed_at/last_rating=NULL`) on every run;
- prints `E2E_SEED_RESULT={...}`; globalSetup forwards ids as `E2E_SEED_*` env vars, but the specs
  also discover the seed by stable marker through the admin API, so no hard dependency on the
  env hand-off.

Idempotency evidence: running the seed twice produced identical `question_id` / `mistake_id` /
`review_item_id`.

The repository's `app/auth/register` endpoint creates a **non-admin** user (`User.is_admin` default
`false`), so it cannot provision the admin session the protected `/api/admin/*` readbacks require;
the seed therefore uses the project's own `bootstrap_temp_admin`, which is also what `.github/
workflows/ci.yml` already uses. This deviation from "prefer register" is deliberate and verified.

## Local same-site runnability

`playwright.config.ts` adds, when `E2E_RESOLVE_HOSTS=1`:

```
--host-resolver-rules=MAP api.ci.test 127.0.0.1, MAP app.ci.test 127.0.0.1
--no-proxy-server
```

`E2E_BASE_URL` = preview origin, `E2E_API_URL` = API origin. The backend readback runs **inside the
page** (`tests/e2e/helpers.ts` `apiGet` → `page.evaluate(fetch(..., {credentials:'include'}))`)
because Node-side `APIRequestContext` does not honor Chromium's resolver and cannot resolve
`api.ci.test`. Full commands: see `docs/ci-local-reproduction.md` → "Local same-site run without
editing `/etc/hosts` (F04)".

## Raw local run

Stack: build `NEXT_PUBLIC_API_URL=http://api.ci.test:18001`; scratch backend
`astra_week4_f04_e2e` on `:18001` (`AUTH_BYPASS=false`, `ALLOWED_ORIGINS=http://app.ci.test:18787`);
workerd preview on `:18787`; `E2E_RESOLVE_HOSTS=1 npx playwright test --workers=1`.

```
[e2e-seed] question=d971a70f-d0a8-45cc-b2aa-26617f57516f review_item=4d41c7cb-6b4a-4de6-b3b2-0c3e20547650 marker=E2E-W4-BUSINESS

Running 5 tests using 1 worker

  ✓  1 [chromium] › tests/e2e/01-login-dashboard.spec.ts:24:5 › E2E-01: 未登录访问工作区跳转登录，登录后进入学习管理首页 (2.8s)
  ✓  2 [chromium] › tests/e2e/02-note-creation.spec.ts:20:5 › E2E-02: 新建笔记并保存后可再次编辑保存 (1.9s)
  ✓  3 [chromium] › tests/e2e/03-capture.spec.ts:15:5 › E2E-03: 错误作答生成待确认错题草稿（真实页面操作 + 后端读回） (3.3s)
  ✓  4 [chromium] › tests/e2e/04-review-flow.spec.ts:23:5 › E2E-04: 复习再答并写入 ReviewRecord（真实页面操作 + 后端读回） (1.9s)
  ✓  5 [chromium] › tests/e2e/05-error-retry.spec.ts:8:5 › E2E-05: 公开笔记页 API 失败时显示错误状态，重试后恢复 (1.2s)

  5 passed (12.0s)
```

A second full run (proving the seed resets the consumed due item and E2E-03 tolerates accumulated
drafts) again produced `5 passed (10.7s)`. Raw logs and the psql readback are in
`evidence/gate/ci/job4-e2e-business*.txt|.log`.

Backend readback after the runs (`astra_week4_f04_e2e`):

```
 context_type | is_correct | count
--------------+------------+-------
 practice     | f          |     3   <- E2E-03 wrong attempts
 review       | t          |     4   <- E2E-04 re-answers

 status    | count
-----------+-------
 converted |     1
 pending   |     3   <- one MistakeDraft per E2E-03 run

 review_records | with_attempt
----------------+--------------
              4 |            4   <- every ReviewRecord links its re-answer attempt
```

## Verification performed

| Check | Command | Result |
|---|---|---|
| Business E2E (raw) | `E2E_RESOLVE_HOSTS=1 … npx playwright test --workers=1` | PASS 5/5, repeated PASS 5/5 |
| Shipped type-check | `npx tsc --noEmit` | exit 0 |
| Test-tree type-check | `npm run test:typecheck` | exit 0 |
| Unit tests | `npm test` | 522 passed (70 files) |
| workerd build | `NEXT_PUBLIC_API_URL=http://api.ci.test:18001 npm run build:cf` | exit 0 |
| Seed idempotency | run seed twice | identical ids |

## NOT_VERIFIED / unresolved

- **Remote GitHub Actions not executed** — no push/commit authorized. The CI `e2e` job will now run
  the seed via `globalSetup` and the rewritten specs; its `E2E_API_URL` default
  (`http://api.ci.test:8001`) matches the CI build URL. This is reasoned, not executed.
- **F01 (CI DB name) still open** — the CI workflow still points at `blog_db`, which the repo guards
  reject; F04 does not change `/etc/hosts`-free CI topology or the DB name. Separate finding.
- **E2E-03 accumulates one `pending` draft per run** on a long-lived DB (expected: the spec creates a
  real wrong attempt each run and asserts by unique answer + attempt_id, so it is order/accumulation
  tolerant). CI uses a fresh service DB each run.
- **Full backend pytest suite not re-run** in this task (out of WRITE SCOPE, unchanged).

## Files changed

- `tests/e2e/seed/seed_week4_business.py` (new)
- `tests/e2e/global-setup.ts` (new)
- `tests/e2e/helpers.ts` (new)
- `tests/e2e/03-capture.spec.ts` (rewritten)
- `tests/e2e/04-review-flow.spec.ts` (rewritten)
- `playwright.config.ts` (globalSetup + `E2E_RESOLVE_HOSTS` resolver, timeout)
- `docs/ci-local-reproduction.md` (local same-site section + deviation refresh)
- `docs/workflows/personal-learning-system-convergence/week4/evidence/pr-17-e2e-business.md` (this)
- `docs/workflows/personal-learning-system-convergence/week4/evidence/gate/ci/job4-e2e-business*` (raw)
