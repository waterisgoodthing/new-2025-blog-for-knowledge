# Week 3 Gate — findings

agent_id: GATE-seed-verify (senior-qa-sdet, verifier) · date: 2026-09-25

## Product findings (code defects)

None found in the Week 3 product code under gate-scope verification. The Gate
matrix six rows all PASS with reproducible evidence, and the final verification
set is green except for documented test-isolation/environment failures below.

## Test / environment findings (not product defects)

### FINDING-1 (INFO, pre-existing) — full backend suite: 4 failures are isolation/env
Full-suite result on a fresh scratch DB (`astra_week3_gate_full`, alembic 032):
`821 passed, 4 failed, 9 skipped, 6 subtests passed`.

Reproduction:
```
python3 scripts/week3-scratch-guard.py run --db-name astra_week3_gate_full \
  -- env PYTHONPATH=. .venv/bin/python -m pytest -q
```
1. `test_lsr03_guarded_runner.py::test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback`
   — psycopg2 IS installed in this venv; the test asserts its absence as a
   runtime-fallback guard. Environment-dependent, pre-existing (baseline 10F
   recorded in pr-09 evidence), not Week 3 code.
2. `test_pr09_verify_http.py::test_public_empty_envelope_explicit` — full-suite
   pollution: an earlier module in the same run leaves `visibility='public'`
   mistakes. Green when run alone on a fresh DB (gate-pr09-http-alone.txt: 27 passed).
3. `test_pr11_dashboard_service.py::test_all_empty_answers_are_honest`
4. `test_pr11_dashboard_service.py::test_partial_service_failure_degrades_without_raising`
   — both assert an empty scratch DB; earlier tests in the same run seed rows.
   Green alone on a fresh DB (gate-isolation-pytest.txt: 3 passed).

Referred evidence: tests/gate-full-pytest.txt, tests/gate-isolation-pytest.txt,
tests/gate-pr09-http-alone.txt, tests/gate-pr09-contract-alone.txt (24 passed).

### FINDING-2 (INFO, pre-existing, deferred) — `npm run test:typecheck` fails on ui-v2
`npx tsc --noEmit` → exit 0 (the canonical Week 3 frontend typecheck).
`npm run test:typecheck` (tsconfig.test.json) → 10 errors, ALL in untracked
pre-existing `src/features/ui-v2/` test files (dashboard/notes/questions/resources/
today). This is PR10F-03, recorded DEFERRED out of Week 3 scope. No Week 3-owned
file appears in the error set.
Reproduction: `npm run test:typecheck`. Evidence: tests/gate-frontend-test-typecheck.txt.

### FINDING-3 (INFO) — reduced-motion media emulation not sticky in gate session
`agent-browser set media "prefers-reduced-motion: reduce"` was applied and a
screenshot captured, but `matchMedia(...)` still reported `false` in this session.
Reduced-motion behavior was already covered by PR-11 real-Chromium evidence
(`pr-11-verify-reduced-motion-loading.png`); the gate screenshot is a current-build
confirmation only. Not a product defect.

## Seed-shape note (resolved during gate execution)
The first seed left two Mistakes without a ReviewItem (`m-priv-archived` etc.),
which made the admin list 500 (`get_mistake` uses `scalar_one`). Fixed the seed
(added a ReviewItem per Mistake) and re-verified; the 500 was a seed artifact,
not a product defect. Final seed: every canonical Mistake has exactly one
ReviewItem (consistent with `MistakeOut.review_item_id` and the PR-09 seed
requirement recorded in pr-09-testfix-7).

## Auth / boundary
Anonymous admin calls all 401 (6 endpoints probed). Public DTO fields = W3-D03
allowlist only (11 fields, no `my_answer`/`version`/`visibility`/`status`/
`source_draft_item_id`/`review_item_id`). Legacy mistake note write frozen with
410. Auth contract unchanged (password login → admin_session cookie still works;
`get_current_admin` still the boundary).