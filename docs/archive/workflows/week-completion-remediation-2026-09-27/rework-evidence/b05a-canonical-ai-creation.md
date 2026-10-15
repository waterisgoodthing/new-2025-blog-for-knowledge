# B05a — Canonical AI-creation contract and incremental schema

Date: 2026-09-27. This IS the B05a deliverable from
[rework-plan.md](../rework-plan.md); it does not change R00/R07 and it gives the
G0/G2/G3 gate reviewers the fixed contract before any wiring was implemented
(indeed, B05b below was built on exactly this contract).

## Product entry

The existing canonical legal entry "从题库记录错题"
(`mistake-draft-entry.tsx`) is the only authorized AI-assisted canonical
creation entry. It stays strictly canonical: a confirmed formal Question, a
user-written wrong answer/`reason`, an optional AI error-interpretation
candidate (informational), and a manual confirm step. It does NOT re-open the
frozen staged Note-style mistake form, does NOT add a second workspace and is
NOT a fully automatic ingest.

Backend domain: `/api/admin/mistakes/ai-candidate` and
`/api/admin/mistakes/ai-confirm` (canonical admin-mistakes domain). Capture's
own AiRun binding is unaffected and remains Capture-targeted.

## Trusted server-side provenance (migration 034 / columns)

The plan specifies an incremental schema change; per the B05a contract this is
an *additive*, revision-bounded migration — not an untouched claim.

```sql
-- 034_ai_run_provenance.py (backend/alembic/versions/034_ai_run_provenance.py)
ALTER TABLE ai_runs
    ADD COLUMN created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN creation_context JSONB,
    ADD COLUMN confirmed_payload_hash VARCHAR(64),
    ADD COLUMN confirmed_at TIMESTAMPTZ;
```

On the server, `creation_context` is created and immutable per-run, built in
`ai_creation_service.build_creation_context`:

```json
{
  "contract": "canonical_ai_creation_v1",
  "purpose": "mistake_canonical_draft",
  "source_question_id": "<uuid>",
  "source_question_version": <int>,
  "input_hash": "<sha256 of {question_id, question_version, my_answer, user_error_reason}>",
  "output_schema": "ErrorInterpretationResponse",
  "prompt_version": "<prompt template version>",
  "input_summary": "truncated"
}
```

Rules that follow from the B05a gate:

- `input_hash` is a normalized server-side hash of the generation inputs.
  `input_summary` is *display-only*; it is never authoritative.
- History rows have NULL `creation_context` and are NOT eligible for canonical
  confirmation (no silent migration for old runs, no owner guessing/backfill).
- `created_by` is server-injected from `get_current_admin` only; no client
  request can pick an owner, and the gateway layer cannot be asked to skip it.
- `review_revision` is reused as the confirm version and verify-expectation.

## Confirmation semantics (single row-locked path)

`ai_creation_service.confirm_canonical_creation` implements the contract in one
place, called ONLY from `/api/admin/mistakes/ai-confirm`:

1. `SELECT … FOR UPDATE` + `populate_existing` on the AiRun row. Every
   confirm/reject/replay path takes the same lock, in the same order, so two
   racing sessions cannot both see "unbound".
2. Verify actor (`run.created_by == actor_id`, else 403), context purpose and
   task type, `status == 'succeeded'`,
   `validation_status ∈ {passed, warning}`, `review_status ≠ 'rejected'`.
3. Compute the confirmed-payload hash server-side over the canonical JSON of
   the confirmed content, never trusting client claim.
4. If `run.target_id` is already set:
   - identical hash → idempotent replay: return the original entity, do NOT
     re-require the current question version, do not re-run the first confirm; 
   - different hash → **409** (never overwrite the target, never return
     somebody else's entity).
5. Otherwise verify `review_revision == run.review_revision`, verify the *live*
   source question (still active, version unchanged) **inside** the same
   transaction, create the MistakeDraft, set `target_type/target_id`, write
   `confirmed_payload_hash/confirmed_at`, accept the review (revision + 1), and
   commit once. A failed create rolls back to a "pending run" that can be
   retried, not to a lost artifact.
6. Retry, reload and concurrent paths all run the same lock order. The retired
   optional `MistakeDraftCreate.source_run_id` field is explicitly rejected with
   a 409 guidance to the canonical endpoint — it can no longer be a bypass.

## Rejected alternatives (included for gate review completeness)

- Reusing `input_summary` as authoritative: rejected — free text, non-salted,
  cannot be compared.
- Teaching `bind_run_to_entity` to also accept an arbitrary source: rejected —
  it is the same two-line helper the reviewer called out; instead it remains
  only for entity-bound Capture flows and the canonical path bypasses it.
- Column-only "add nullable then defer" — rejected. The contract needs an
  immutable JSONB and a hash column; both are additive (append-only, old rows
  readable as NULL, no destructive migration), so this is the minimal diff.
