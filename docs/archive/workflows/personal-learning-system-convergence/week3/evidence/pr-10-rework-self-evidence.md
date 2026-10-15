# PR-10 rework — PFV-01 (MEDIUM) + PFV-02 (LOW)

agent_id: PR-10-rework · profile: senior-backend-engineer · role: implementer · date: 2026-09-25
Scratch DB: `astra_week3_pr10_rw` (guard-created, `alembic upgrade head` -> `031`).
Base findings: `evidence/reviews/pr-10-findings.md`.

## Changes

| File | Change |
| --- | --- |
| `backend/app/services/kp_analytics_service.py` | `review_link` now joins `questions` and filters `Question.status == 'active'`; converted `.subquery()` -> `.cte()` so the review path is defined once (PFV-02). |
| `backend/tests/test_pr10_kp_analytics_service.py` | New `test_archived_question_active_mistake_review_path_is_excluded`: archived Question + active Mistake + due ReviewItem + lapse rating -> all review metrics 0. |
| `week3/evidence/tests/pr-10-rework-*.txt`, `week3/evidence/sql/pr-10-rework-analytics-query.txt` | Re-run evidence (this file). |

No other product file, `src/**`, model, migration, or git write was touched.

## PFV-01 — archived Question excluded on review path

`review_link` gained `JOIN questions ON questions.id = mistakes.question_id` and
`WHERE mistakes.status = 'active' AND questions.status = 'active'`. Same
single-statement aggregate, same stable `knowledge_point_id ASC` sort, zero
denominator still `0.0`. Verified by the verifier's own repro
(`evidence/tests/pr-10-verify-archived-question-review-path.py`):

- before: `review_count=3 due_count=1 lapse_count=2 attempt_count=0`
- after:  `review_count=0 due_count=0 lapse_count=0 attempt_count=0`

## PFV-02 — duplicated review subquery removed

Emitted SQL now defines the review path once: `WITH anon_5 AS (...)` appears
exactly once and is referenced by both `review_agg` and `due_agg`
(`evidence/sql/pr-10-rework-analytics-query.txt`); still a single analytics
statement (N=1 -> 1, N=6 -> 1).

## Verification (all on `astra_week3_pr10_rw`)

| Evidence | Result |
| --- | --- |
| `tests/pr-10-rework-targeted-pytest.txt` | 33 passed (impl service incl. new test + verify matrix + contract + http + verify contract) |
| `tests/pr-10-rework-contracts-lock-pytest.txt` | 53 passed (`test_week3_contracts.py`) |
| `tests/pr-10-rework-repro-archived-question.txt` | archived-question review path -> 0/0/0 |
| `sql/pr-10-rework-analytics-query.txt` | `WITH anon_5 AS` once; 1 statement |

## Scope / unresolved

- Write scope respected: `backend/app/services/kp_analytics_service.py`,
  `backend/tests/test_pr10_kp_analytics_service.py`, `week3/evidence/**` only.
- `kp_analytics_service.py` and its test file are untracked, so `git diff` is
  empty by construction; edits are confined to the named files.
- PFV-03 (pre-existing unrelated ui-v2 tsc errors) intentionally untouched.
