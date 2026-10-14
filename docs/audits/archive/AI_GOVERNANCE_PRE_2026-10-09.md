# AI Governance — Run Target Linkage

This document defines when an `ai_runs` row must be linked to the business
entity it operates on, when linkage is intentionally absent, and how
creation-type flows backfill linkage.

## Background

Every AI model call goes through `backend/app/services/ai_gateway.py`
(`call_text`, `call_vision`, `call_general`, `call_stream`). Registered task
types create a business `AiRun` record via `_start_run_record` →
`ai_run_service.start_ai_run`. The `ai_runs.target_type` / `ai_runs.target_id`
columns are nullable; this document pins down when they are populated.

`target_type` is the entity kind (`"Capture"`, `"MistakeDraft"`, …); `target_id`
is the entity id as a string. `_finish_run_record` and `retry_ai_run` do not
need special handling: retry copies the parent's target, and finish only
terminates the row already created with its target.

Every gateway call returns the business run id on `GatewayCallResult.run_id`
(``None`` when the task type is unregistered or the run row could not be
written). Callers that persist a user-confirmed artifact must carry that id
into the save request so the linkage can be enforced server-side.

## Classification criteria

### Persisted target-linked

The AI output is written into (or offered as the direct draft of) a durable
business entity, and the run is traceable to that entity. These runs **must**
pass `target_type`/`target_id` at creation.

### Transient preview — exempt

The output is streamed or returned to the user for preview and is **not**
persisted by the system; nothing durable exists to link. These paths are
exempt from `AiRun` target linkage. If such a path should be audited later, it
must first become persisted, at which point this classification must be revised.

### Creation-type — NULL then backfill

The target entity does not exist yet when the AI call runs (for example,
generating a draft that may become a brand-new record).

- The `AiRun` is created with `target_id = NULL` (and `target_type` may be set
  to the intended entity kind, or left NULL until known).
- On user confirmation/save, the owning service calls
  `ai_run_service.bind_run_to_entity(db, run_id, entity_type=...,
  entity_id=...)` **inside the same transaction** that creates the entity, so
  the entity and its provenance commit atomically. If the run is missing,
  failed, rejected, of a non-creation task type, or already bound to a
  different target, the save is rejected and rolls back.
- If the suggestion is abandoned/rejected, no binding happens and `target_id`
  stays `NULL`. This is a **valid terminal state**, not an error or a data gap.
- The low-level `backfill_ai_run_target` helper still exists for callers that
  only need to set a target on a known run; `bind_run_to_entity` is the
  validated entry point used by the canonical save path.

**WIRED (F05):** the canonical `POST /api/admin/mistake-drafts` creation
endpoint accepts an optional `source_run_id`. When present, it validates the
run (succeeded, not rejected, allowed creation task type, no conflicting
target) and binds it to the newly created `MistakeDraft` in the same
transaction. The staged generation responses (`QuestionDraftResponse`,
`ErrorInterpretationResponse`, `FinalAnalysisResponse`) now carry
`source_run_id`, so a client can generate → save with provenance. The legacy
staged-note save remains frozen (W3-D09); this contract governs the canonical
draft save, not the frozen path.

## Current feature classification

| Feature | Call path | Task type(s) | Classification |
| --- | --- | --- | --- |
| Capture recognition (OCR/vision) | `capture_recognition.recognize_image` → `call_vision` | `capture_recognition` | Persisted target-linked to `Capture` (passes `target_type="Capture"`, `target_id=<capture_id>`) |
| Capture AI draft | `capture_ai_draft.draft_mistake` → `call_text` | `capture_draft` | Persisted target-linked to `Capture` (passes `target_type="Capture"`, `target_id=<capture_id>`) |
| Note polish / summarize / translate / title / tags / … | `routers/ai_polish.py` → `ai_polish_service.polish_stream` | none (bypasses gateway) | **Exempt**: transient streaming preview, not persisted, no `AiRun` created |
| Diagram structured / fallback | `diagram_service` → `call_text` | `diagram_structured`, `diagram_fallback` | Not yet linked (out of PR-19 scope). Follow the transient/persisted rule when linkage is added: a persisted diagram record is target-linked; an inline preview is exempt |
| Mistake staged question / interpretation / final analysis | `mistake_staged_service` → `call_text`/`call_vision` | `mistake_question_draft`, `mistake_error_interpretation`, `mistake_final_analysis` | Creation-type: `target_id = NULL` at generation; response carries `source_run_id`; the canonical `POST /api/admin/mistake-drafts` save binds the run to the created draft |
| Analyze / variant / knowledge card / summary / prompt test | `routers/ai.py` → `call_text`/`call_vision` | `analyze_mistake`, `analyze_text`, `generate_variant`, `generate_knowledge_card`, `knowledge_summary`, `prompt_test` | Not yet linked (out of PR-19 scope) |
| Recommendation | `recommendation.py` → `call_general` | `recommendation` | Not yet linked (out of PR-19 scope) |
| Netease reason | `netease_service` → `call_text` | `netease_reason` | Not yet linked (out of PR-19 scope) |

"Not yet linked" means the call site does not currently pass target kwargs and
therefore records `target_id = NULL`. That is a known coverage gap to close in
later work, not an exempt classification. No persisted-canonical call site is
left unclassified: every gateway caller is either linked, exempt, or explicitly
listed here as a gap.

### Why Capture draft links to `Capture`, not to `MistakeDraft`/`Question`

The AI draft call acts on the Capture: it consumes the capture's recognized
text and stores its suggestion on the capture row. The capture may never be
converted, and the question/mistake draft is created later by
`capture_service.convert_capture` from human-confirmed data. Linking the
`capture_draft` AiRun to `target_type="Capture"` (the entity the AI actually
operated on) is therefore the intended classification, and the run is
intentionally not relinked to the downstream `MistakeDraft`/`QuestionDraft`.

## Backfill contract

Creation-type flows follow this contract:

1. Create the `AiRun` with `target_id = NULL` while the entity does not exist.
2. When the user confirms and the entity is created, call
   `ai_run_service.backfill_ai_run_target(db, run_id, target_id,
   target_type=...)`, which updates the existing `ai_runs` row, flushes, and
   returns False when the run does not exist. No new migration is required
   because the columns already exist.
3. If the suggestion is abandoned, no backfill happens and `target_id` remains
   `NULL`. Consumers must treat `NULL` as "unlinked / not confirmed", not as a
   defect.

**NOT_YET_WIRED:** the helper is implemented and unit-tested, but no production
confirmation endpoint invokes it yet. The contract is defined; the integration
is prospective until a confirmation flow calls the helper.

Retry semantics are preserved: `retry_ai_run` copies `target_type`/`target_id`
from the parent run, so a backfilled target propagates to retries.
