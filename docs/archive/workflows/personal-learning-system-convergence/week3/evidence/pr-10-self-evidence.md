# PR-10 — Canonical KP analytics — self evidence

agent_id: PR-10-impl · profile: senior-backend-engineer · role: implementer · date: 2026-09-25

## Delivered

| File | Change |
| --- | --- |
| `backend/app/schemas/kp_analytics.py` | New `KnowledgePointAnalyticsItem` (contract field names/order: `knowledge_point_id` + `W3_D05_METRICS`) |
| `backend/app/services/kp_analytics_service.py` | New service: pure `compute_attempt_rates` / `KP_ANALYTICS_SORT_KEY` / `kp_analytics_sort_key` + `get_knowledge_point_analytics` |
| `backend/app/routers/knowledge_points.py` | New `GET /api/admin/knowledge-points/analytics` (thin, admin-only router dependency), registered before `/{knowledge_point_id}` |
| `backend/tests/test_pr10_kp_analytics_contract.py` | 9 no-DB tests: schema, sort, route registration/order, admin gate, anonymous 401 |
| `backend/tests/test_pr10_kp_analytics_http.py` | 2 DB tests: anonymous 401/403 + admin 200 payload field set |
| `backend/tests/test_pr10_kp_analytics_service.py` | 6 DB fixture tests (see matrix) |
| `backend/tests/_pr10_n1_evidence.py` | N+1 query-count evidence script (guard-run) |

## Semantics implemented (W3-D05 / design.md D7)

- `attempt_count` / `wrong_count`: canonical `Attempt` with `context_type='practice'` joined via `QuestionKnowledgePoint`; `Question.status='active'` only. `review`/`editor_check` excluded.
- `graded = attempt_count` (`is_correct` NOT NULL); `accuracy`/`wrong_rate` via non-zero denominator, zero samples -> `0.0` (float, not None/NaN).
- `review_count` = COUNT(`review_records` -> `review_items` -> `mistakes` -> KP) (design.md D7); `due_count` = active `ReviewItem` with `next_review_at <= now`; `lapse_count` = `ReviewRecord.rating <= 2` lifetime.
- Mistake->KP via canonical `knowledge_point_links(target_type='mistake', target_id=str(id))`.
- Multi-KP question contributes full observation to every linked KP (no fractional split).
- Excludes archived Question, archived Mistake, inactive KP.
- Sort: `wrong_rate DESC, lapse_count DESC, due_count DESC, knowledge_point_id ASC`.

## Fixture matrix (all PASS)

| Case | Expectation |
| --- | --- |
| 2 correct + 1 wrong practice + review + editor_check | attempt=3 wrong=1 acc=2/3 rate=1/3 |
| no attempts | attempt=0 wrong=0 acc=0.0 rate=0.0 (float) |
| due active + mastered + future active, ratings 1/2/4/5/3 | review=5 lapse=2 due=1 |
| archived question attempt / archived mistake review / archived KP | excluded (active KP zeros; inactive KP absent) |
| multi-KP question wrong | each KP attempt=1 wrong=1; tie -> id ASC |
| 1 vs 25 active KPs | analytics statements = 1 vs 1 (no N+1) |

## Evidence (docs/.../week3/evidence/tests/)

- `pr-10-all-pytest.txt` — 17 passed (contract+http+service, guard-run).
- `pr-10-contract-pytest.txt` — 9 passed.
- `pr-10-http-pytest.txt` — 2 passed.
- `pr-10-service-pytest.txt` — 6 passed.
- `pr-10-contracts-lock-pytest.txt` — 53 passed (`test_week3_contracts.py` still green).
- `pr-10-n1-query-count.txt` — `1 active KP = 1, 25 active KPs = 1`.

Scratch DB: `astra_week3_pr10` (created locally, `alembic upgrade head` -> 031), all DB tests through
`scripts/week3-scratch-guard.py run --db-name astra_week3_pr10`.

## Scope / unresolved

- Write scope respected: services/routers/schemas/tests + this evidence only; no models, alembic, src, or git writes.
- Unresolved (for PR-11 client/Dashboard): this task is backend-only; `src/lib/api` DTO and weak_top3 rendering belong to PR-10-impl-client / PR-11.
