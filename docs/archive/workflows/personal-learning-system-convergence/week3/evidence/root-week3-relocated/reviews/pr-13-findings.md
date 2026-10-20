# PR-13 verification findings (agent PR-13-verify, senior-qa-sdet)

Scratch DB: `astra_week3_pr13_verify` (fresh; `alembic upgrade head` → 032 via guard).
Result: **no BLOCKER / HIGH / MEDIUM defects**. All acceptance items reproduced PASS.
The items below are LOW/INFO observations for the reviewer / G4 gate, not fixes.

## PR13V-01 — LOW — No-KP active Questions are silently dropped from metadata

- Evidence: `week3/evidence/tests/pr-13-verify-pytest.txt`
  (`test_b_question_without_kp_is_not_a_candidate`).
- Behaviour: an active Question with no `QuestionKnowledgePoint` link is never a
  candidate, and `raw_candidate_count` counts only KP-linked Questions. When a
  no-KP Question coexists with KP-linked ones, the dropped Question is not
  reflected anywhere in `empty_metadata`.
- Assessment: deterministic and documented in the implementer self-evidence;
  `PracticeItem.knowledge_point_id` is non-nullable so exclusion is defensible.
  Flag only if "honest Empty metadata" is expected to disclose skipped no-KP rows.
- Product-code fix: none applied (verifier role).

## PR13V-02 — LOW — Mastered exclusion ignores `Mistake.status`

- Evidence: `week3/evidence/tests/pr-13-verify-pytest.txt`
  (`test_b_mastered_archived_mistake_still_excludes_observation`).
- Behaviour: `select(Mistake.question_id).join(ReviewItem).where(ReviewItem.state=='mastered')`
  has no `Mistake.status` filter, so an `archived` canonical Mistake whose
  ReviewItem is mastered still excludes the Question.
- Assessment: matches the literal task text ("任一关联 canonical Mistake") and the
  implementer note. Confirm whether archived Mistakes should be out of scope.

## PR13V-03 — INFO — `PRACTICE_MAX_ITEMS = 10` is effectively unreachable

- Evidence: `test_a_target_count_function_matrix` (`10 -> 3`, `11 -> 3`).
- Because target is 3 whenever eligible ≥ 3, the returned count never exceeds 3;
  the 0..10 contract bound (`PRACTICE_ITEMS_MAX = 10`) holds trivially. Consistent
  with W3-D05 "eligible ≥3 → target 3"; recorded for clarity only.

## PR13V-04 — INFO — Metadata three-way agreement is schema↔client; contract types it as a dict

- Evidence: `test_d2_dto_three_way_agreement`, `week3/evidence/api/pr-13-verify-contract.txt`.
- `week3_contracts_support.PracticeResponse` declares `empty_metadata: dict[str, Any]`
  (no explicit field constant), so exact metadata field locking is verified between
  `app/schemas/practice.py` and `src/lib/api/practice.ts`; the W3 contract locks the
  top-level response fields (`items`, `empty_metadata`). No mismatch found.

## PR13V-05 — INFO — `selection_reason` is knowledge-point-level

- Multiple items sharing the same chosen KP carry the same reason, derived from that
  KP's PR-10 metrics (wrong_rate → lapse → due → stable fallback). Intended by design.
