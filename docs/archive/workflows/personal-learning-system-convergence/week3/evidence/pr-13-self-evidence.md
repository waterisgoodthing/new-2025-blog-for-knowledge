# PR-13 self-evidence — daily practice

**agent_id:** PR-13-impl · **profile:** senior-recommendation-engineer · **role:** implementer
**scratch DB:** `astra_week3_pr13` (created fresh; `alembic upgrade head` → 032 via guard)

## Deliverables

| Artifact | Path |
| --- | --- |
| Selection service | `backend/app/services/practice_service.py` |
| DTOs | `backend/app/schemas/practice.py` (`PracticeItem`, `PracticeEmptyMetadata`, `PracticeTodayResponse`) |
| Admin endpoint | `backend/app/routers/practice.py` → `GET /api/admin/practice/today` |
| Registration | `backend/main.py` (import + `include_router(practice.router)`) |
| Service tests | `backend/tests/test_pr13_practice_service.py` |
| HTTP contract tests | `backend/tests/test_pr13_practice_http.py` |
| Read-only evidence script | `backend/tests/_pr13_attempt_count_evidence.py` |

## Locked semantics (W3-D05)

- weak-KP priority comes from `kp_analytics_service.get_knowledge_point_analytics`
  (PR-10 authority); no second weighting exists in the new code.
- candidates = `active` Question linked through `QuestionKnowledgePoint` to
  `active` KnowledgePoint.
- rolling window = previous `7 * 24` hours (`PRACTICE_WINDOW_HOURS`), excludes any
  Question with a `practice`-context Attempt in `[now-window, now]`.
- mastered exclusion: any canonical `Mistake.question_id` whose `ReviewItem.state='mastered'`.
- eligible ≥ 3 → target 3; else actual count; hard cap `PRACTICE_MAX_ITEMS = 10`.
- final stable ordering tail: `knowledge_point_id`, then `question_id`.
- selection reasons: `weak_kp_wrong_rate` / `weak_kp_lapse` / `weak_kp_due` /
  `stable_order_fallback` (deterministic; derived from the chosen KP's PR-10 metrics).
- `empty_metadata` is always present and honest:
  `reason ∈ {candidates_returned, no_eligible_candidates, all_candidates_excluded}`,
  plus raw/recent/mastered/eligible/target/returned counts and `window_hours`.
- read-only: service issues only `SELECT`s; no Attempt is created.

## Evidence

| Evidence | File | Result |
| --- | --- | --- |
| Targeted pytest (service + HTTP) | `evidence/tests/pr-13-practice-pytest.txt` | **17 passed** |
| Week 3 contracts regression | `evidence/tests/pr-13-week3-contracts-pytest.txt` | **53 passed** |
| Attempt count unchanged | `evidence/tests/pr-13-attempt-count.txt` | `{"attempts_before":0,"attempts_after":0,"unchanged":true}` |
| Write-scope git status | `evidence/tests/pr-13-git-status.txt` | see file |

Command (all via guard):

```
python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr13 \
    -- backend/.venv/bin/python -m pytest \
       tests/test_pr13_practice_service.py tests/test_pr13_practice_http.py -q
```

## Interpretation notes (for verifier / reviewer)

1. **No-KP fallback**: a Question without any active KP link cannot populate the
   required `knowledge_point_id`, so it is not a candidate; when only such
   Questions exist the response is deterministic Empty
   (`reason=no_eligible_candidates`). When candidates exist but all KP metrics are
   zero, ordering falls back deterministically to `(kp_id, question_id)` with
   `selection_reason=stable_order_fallback`.
2. **Mastered scope**: the task text says “any linked canonical Mistake”, without a
   `Mistake.status` qualifier, so the mastery query does not filter Mistake status.
   Flag if a status filter is intended.
3. **main.py touched**: route registration requires the composition root, which is
   not inside the declared write globs (`services/routers/schemas/tests`). The edit
   is two lines (import token + `include_router`); the pre-existing dirty changes in
   `backend/main.py` (revision 032, admin_notes/public_mistakes) were preserved.
