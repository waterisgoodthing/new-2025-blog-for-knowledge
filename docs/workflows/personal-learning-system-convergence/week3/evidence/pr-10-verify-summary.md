# PR-10 independent verification — summary

STATUS 2026-09-22: PFV-01 + PFV-02 **CLOSED** (fixed in rework); verdict remains
**PASS** based on current code and rework evidence. PFV-03 remains pre-existing/out of scope.

agent_id: PR-10-verify · profile: senior-qa-sdet · role: verifier · date: 2026-09-25
Scratch DB: `astra_week3_pr10_verify` (guard-created, `alembic upgrade head` -> `031`).
No product code changed. No git writes.

## Verdict: PASS (with one MEDIUM adjudication note, PFV-01)

## A — metric semantic fixture matrix

| # | Case | Result |
| --- | --- | --- |
| A1 | correct/wrong practice attempts -> counts + rates | PASS |
| A2 | `context_type='review'` / `editor_check` excluded from practice | PASS |
| A3 | no attempt / only-review -> accuracy=0.0 wrong_rate=0.0 float (not None/NaN) | PASS |
| A4 | due vs future vs mastered + `<= now` boundary, no double count | PASS |
| A5 | `lapse_count` lifetime `rating<=2`; 2 counts, 3 does not | PASS |
| A6 | multi-KP question full observation per KP (no fractional split) | PASS |
| A7 | archived Question/Mistake + inactive KP excluded (attempt path) | PASS |
| A8 | tie -> `knowledge_point_id ASC`, deterministic | PASS |

Independent tests: `backend/tests/test_pr10_verify_matrix.py` (9 passed).

## B — N+1

`evidence/sql/pr-10-verify-analytics-query.txt`: N=1 and N=6 active KPs each
emit exactly 1 analytics statement; full SQL captured (single `SELECT` with
coalesced outer joins). `test_b_*` additionally checks N in {1,3,6,12} all = 1.

## C — contract & permissions

`evidence/api/pr-10-verify-analytics-http.txt`: anonymous 401, admin login 200,
admin GET 200, exactly 8 fields (`knowledge_point_id` + W3_D05 metrics).
`backend/tests/test_pr10_verify_contract.py` (6 passed) proves three-way parity:
backend `KnowledgePointAnalyticsItem` == `week3_contracts_support` W3-D05 set ==
frontend `KpAnalytics` interface / `KP_ANALYTICS_METRIC_FIELDS`; route GET-only
and requires `get_current_admin`; analytics route precedes `{knowledge_point_id}`.

## D — source search

`evidence/tests/pr-10-verify-source-search.txt`: no weight/ML/trend/AI tokens,
no sklearn/numpy/etc.; service imports only sqlalchemy + app models/schemas; sort
tuple in service == contract; no backend dependency change.

## Regression

`evidence/tests/pr-10-verify-impl-regression.txt`: implementer PR-10 suites +
`test_week3_contracts.py` re-run green (70 passed) on the verify scratch DB.
`evidence/tests/pr-10-verify-client-vitest.txt`: client vitest 3/3.
`evidence/tests/pr-10-verify-client-tsc.txt`: `test:typecheck` has 10 errors, all
in unrelated untracked ui-v2 tests (0 in `knowledge-points`) — PFV-03.

## Findings

See `evidence/reviews/pr-10-findings.md`. PFV-01 MEDIUM (archived-Question review
path not excluded; needs D7 wording adjudication), PFV-02 LOW (duplicated review
subquery), PFV-03 INFO (pre-existing unrelated tsc errors).
