# Week 3 Gate matrix — evidence record

agent_id: GATE-seed-verify (senior-qa-sdet, verifier)
date: 2026-09-25
scratch DB: `astra_week3_gate` (guarded via `scripts/week3-scratch-guard.py`, alembic head 032)
backend: uvicorn 127.0.0.1:8001 on astra_week3_gate (log: browser/gate-backend.log)

## Seed inventory (README §5)

Two+ KnowledgePoints with deliberately different weakness histories:
- GATE Alpha (kp 137): wrong_rate 0.8, lapse 2, due 2 (weak)
- GATE Beta  (kp 138): wrong_rate 0.2, lapse 0, due 0 (strong)
- GATE Gamma (kp 139): wrong_rate 0.5, lapse 0, due 0
- GATE Delta (kp 140): wrong_rate 0.5, lapse 0, due 0 (tie with Gamma, id > Gamma)

Questions: active eligible (q-a1, q-a2, q-b1, q-extra), archived (q-archived),
recently attempted in-window (q-recent), mastered-linked (q-mastered).

ReviewItems: due (ri-due1, ri-due2), future (ri-future, ri-c-future, ri-d-future),
mastered (ri-mastered, 1 rating-5 record new_state=mastered, 30 min ago).

Mistakes: public canonical (m-pub1, m-pub2), private canonical (m-priv1, m-priv-c,
m-priv-d, m-mastered), archived private (m-priv-archived), legacy Note mistakes
(gate-legacy-mistake-1 published+visible, gate-legacy-mistake-2 unpublished).

Note: one canonical Note (gate-canonical-note) pre-linked to Alpha via migration 032.

Admin user: gate-admin (is_admin=true).

## Matrix results

| Q | Invariant | Evidence | Result |
|---|-----------|----------|--------|
| 1 | Review today == canonical due active ReviewItems | sql/gate-matrix-recompute.json (Q1_review_today: true); api/gate-matrix-http.json (review_today_count=2, section_actions.review.count=2, reason=due_reviews_pending) | PASS |
| 2 | Practice today == PR-13 eligible, weak/recent/mastered filters | sql/gate-matrix-recompute.json (Q2_practice_today: true; raw 6, recent_excluded 2, mastered_excluded 1, eligible 3); api (practice 3 items weak_kp_wrong_rate) | PASS |
| 3 | Weakest KP == PR-10 locked ordering + stable tie-breaker | sql/gate-matrix-recompute.json (Q3_weakest_kp: true; Alpha first; Gamma kp 139 before Delta kp 140 at equal wrong_rate 0.5 — knowledge_point_id ASC tie-breaker) | PASS |
| 4 | Public mistake ownership canonical | api/gate-matrix-http.json (total=2 public canonical; titles m-pub1/m-pub2; no private/legacy/mastered; empty=false); browser walkthrough populated/Empty; sql/gate-public-negative.sql | PASS |
| 5 | Note↔KP canonical (032) | api/gate-q5.json (link persists in note_knowledge_points, duplicate idempotent, unlink 204, 404 missing note/KP, raw duplicate PK + FK IntegrityError, legacy freeze 410) | PASS |
| 6 | Boundary safe | api/gate-matrix-http.json (anonymous admin 401 x6; public DTO allowlist only 11 fields); legacy freeze 410 | PASS |

Evidence files: sql/gate-matrix-recompute.json, api/gate-matrix-http.json,
api/gate-q5.json, sql/gate-matrix-recompute.py (source), sql/gate-seed.py (source).