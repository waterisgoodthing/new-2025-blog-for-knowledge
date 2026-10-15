# PR-10 independent verification — findings

agent_id: PR-10-verify · profile: senior-qa-sdet · role: verifier · date: 2026-09-25

Verification conclusion: **PASS** on all eight A-matrix items, B (N+1), C (contract/
permission/DTO), and D (no weight/ML/trend/AI). Findings below are non-blocking
semantic/perf observations plus one pre-existing unrelated type error set.

Status update 2026-09-22: PFV-01 and PFV-02 were fixed in the PR-10 rework and are
now **CLOSED** (evidence below). PFV-03 remains pre-existing and out of PR-10 scope.

| id | severity | item | status |
| --- | --- | --- | --- |
| PFV-01 | MEDIUM | Archived-Question review path is not excluded | **CLOSED** — fixed in rework, repro `3/1/2 -> 0/0/0` |
| PFV-02 | LOW | Review/due subquery is duplicated in one statement | **CLOSED** — fixed in rework, single `WITH`/`.cte()` |
| PFV-03 | INFO | `test:typecheck` fails in 10 unrelated untracked ui-v2 tests | PRE-EXISTING / out of PR-10 scope |

## PFV-01 — MEDIUM — Archived-Question review path still contributes — **CLOSED**

**Contract.** design.md D7: "Archived Question/Mistake 与 inactive KP 不参与第一版
统计"; week3/pr-10.md acceptance: "排除 archived Question/Mistake、inactive KP".

**Observation.** The attempt path filters `questions.status='active'`, but the
review path (`knowledge_point_links -> mistakes -> review_items -> review_records`)
filters only `mistakes.status='active'` and never joins `questions`. An ACTIVE
Mistake whose source Question is ARCHIVED still contributes review metrics.

**Repro (committed runtime evidence).**
`evidence/tests/pr-10-verify-archived-question-review-path.py` against
`astra_week3_pr10_verify` prints:

```
archived-question / active-mistake review path -> review_count=3 due_count=1 lapse_count=2 attempt_count=0
```

**Assessment.** Defensible reading: the canonical owner of review history is the
active Mistake, so archiving the Question need not erase it. Strict reading of
D7 groups "Archived Question" with archived entities and expects exclusion. The
implementer's own fixture only exercises archived-Question on the attempt path
and archived-Mistake on the review path, so the matrix never contradicts itself,
but the acceptance wording is broader than the implementation. No NaN, no
instability, no leakage. Recommendation: main agent adjudicate D7 wording; if
exclusion is intended, add `Question.status='active'` to the review path and a
fixture. Not a blocker for the listed acceptance items.

**Resolution (CLOSED, 2026-09-22, rework).** Exclusion was implemented:
`backend/app/services/kp_analytics_service.py` `review_link` now joins `questions`
and filters `Question.status == 'active'`. The verifier's own repro against the
reworked service now prints `review_count=0 due_count=0 lapse_count=0
attempt_count=0` (was `3/1/2`), i.e. `3/1/2 -> 0/0/0`. Evidence:
`evidence/tests/pr-10-rework-repro-archived-question.txt` and
`evidence/pr-10-rework-self-evidence.md`.

## PFV-02 — LOW — duplicated review subquery — **CLOSED**

The emitted SQL embeds the identical `anon_5` (knowledge_point_links -> mistakes
-> review_items -> review_records) subquery twice, once inside `review_agg` and
once inside `due_agg`. It is still a single round-trip (no N+1); the DB may
evaluate the shared subquery once. Recorded as a future optimization note only.

**Resolution (CLOSED, 2026-09-22, rework).** The subquery was converted to a
single `.cte()`, so the emitted SQL now defines the review path once
(`WITH anon_5 AS (...)` referenced by both `review_agg` and `due_agg`) while
remaining a single analytics statement (N=1 -> 1, N=6 -> 1). Evidence:
`evidence/sql/pr-10-rework-analytics-query.txt` and
`evidence/pr-10-rework-self-evidence.md`.

## PFV-03 — INFO — pre-existing unrelated type errors

`npm run test:typecheck` (`tsc --project tsconfig.test.json`) exits 2 with 10
errors, all in untracked `src/features/ui-v2/{dashboard,notes,questions,
resources,today}/*.test.tsx`. Zero errors mention `knowledge-points`. These files
are unrelated future-UI work and are outside PR-10's write scope. The PR-10
client itself passes its targeted vitest (3/3) and the field-parity check.

## Verified clean (no finding)

- Practice metrics, review-context exclusion, zero denominator -> 0.0 float.
- due/future/mastered and `<= now` boundary, distinct-item due counting.
- lapse lifetime `rating <= 2` with rating=2 counted, rating=3 not.
- Multi-KP full observation per KP (no fractional split).
- Archived Question/Mistake and inactive KP exclusion on the attempt path.
- Stable `knowledge_point_id ASC` tie-break, deterministic across runs.
- Single analytics statement for N and 2N active KPs (no per-KP N+1).
- admin-only 401 anonymous / 200 admin; 8-field payload; backend schema,
  W3-D05 contract and frontend DTO three-way consistent.
- No weight/ML/trend/AI tokens, no new backend dependency.
