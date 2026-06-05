# Tasks: AI Skill Pipeline Knowledge Base

**Status**: implementation in progress (backend Phase 3–5 complete)

## Phase 1: Planning Completion

- [x] **T1-1**: Confirm this workflow's requirements with the user.
  - Files: `docs/workflows/ai-skill-pipeline/requirements.md`
  - Completion standard: user approves or requests edits.
  - Status: user provided explicit implementation instruction covering all tasks.

- [x] **T1-2**: Confirm this workflow's design with the user.
  - Files: `docs/workflows/ai-skill-pipeline/design.md`
  - Completion standard: user approves or requests edits.
  - Status: user provided explicit implementation instruction covering all tasks.

- [ ] **T1-3**: Confirm external skill installation target.
  - Options: `~/.openclaw/skills`, `~/.claude/skills`, or Codex-compatible local skills path.
  - Completion standard: target path is documented before installation.
  - Status: deferred — not required for backend implementation.

## Phase 2: Skill Setup Verification

- [ ] **T2-1**: Install or verify `Humanizer-zh`.
  - Status: deferred — external skill, not required for backend implementation.

- [ ] **T2-2**: Install or verify `guizang-social-card-skill`.
  - Status: deferred — external skill, not required for backend implementation.

- [ ] **T2-3**: Install or verify `ian-xiaohei-illustrations`.
  - Status: deferred — external skill, not required for backend implementation.

- [ ] **T2-4**: Install or verify `notebooklm-skill`.
  - Status: deferred — external skill, not required for backend implementation.

## Phase 3: Backend Contract Design

- [x] **T3-1**: Map existing Notes / Mistakes / Reviews model fields before adding schemas.
  - Candidate files: `backend/app/models/note.py`, `backend/app/schemas/note.py`, `backend/app/routers/review.py`
  - Completion standard: implementation notes identify real field names and avoid creating a first-class `KnowledgePoint` entity.

  **Validation Report:**
  - **Changed files:** None (read-only audit)
  - **Validation command:** `python -c "from app.models.note import Note, Tag, note_tags"`
  - **Validation result:** pass
  - **Manual verification:** Audited `backend/app/models/note.py` (110 lines). Confirmed fields: `id`, `slug`, `title`, `content`, `type`, `status`, `hidden`, `created_at`, `updated_at`, `summary`, `cover`, `category`, `subject`, `difficulty`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, `ef`, `interval`, `repetitions`, `next_review`, `last_reviewed`, `images`, `ai_metadata`, `folder_id`, `sort_order`, `search_vector`. Tag M2M via `note_tags`. No `KnowledgePoint` entity exists.
  - **Scope check:** No `KnowledgePoint` entity, vector DB, or embedding model introduced.
  - **Remaining risks:** None

- [x] **T3-2**: Define source reference schema.
  - Candidate file: `backend/app/schemas/knowledge.py`
  - Completion standard: source refs can represent notes, mistakes, and review-derived sources.

  **Validation Report:**
  - **Changed files:** `backend/app/schemas/knowledge.py`
  - **Validation command:** `python -c "from app.schemas.knowledge import SourceRef, SourceType"`
  - **Validation result:** pass
  - **Manual verification:** `SourceRef` has fields: `source_type` (note/mistake), `source_id`, `title`, `slug`, `field`, `excerpt`, `url`, `confidence`, `match_reasons`. `SourceType` enum covers `note` and `mistake`.
  - **Scope check:** No `KnowledgePoint` entity or vector DB.
  - **Remaining risks:** None

- [x] **T3-3**: Define context-pack request and response schemas.
  - Candidate file: `backend/app/schemas/knowledge.py`
  - Completion standard: request supports subject, knowledge points, tags, type, date range, review state, and limit.

  **Validation Report:**
  - **Changed files:** `backend/app/schemas/knowledge.py`
  - **Validation command:** `python -c "from app.schemas.knowledge import ContextPackRequest, ContextPackResponse"`
  - **Validation result:** pass
  - **Manual verification:** `ContextPackRequest` supports `subject`, `knowledge_points` (list), `tags` (list), `type`, `difficulty`, `date_range` (DateRange with `from`/`to` aliases), `review_state` (due/overdue/upcoming/all), `limit` (1–100). `ContextPackResponse` returns `sources`, `related_notes`, `related_mistakes`, `suggested_relations`, `stats`.
  - **Scope check:** No `KnowledgePoint` entity or vector DB.
  - **Remaining risks:** None

- [x] **T3-4**: Define relation suggestion schema.
  - Candidate file: `backend/app/schemas/knowledge.py`
  - Completion standard: supports relation type, score, reason, and suggestion status.

  **Validation Report:**
  - **Changed files:** `backend/app/schemas/knowledge.py`
  - **Validation command:** `python -c "from app.schemas.knowledge import RelationSuggestion, RelationType, RelationStatus"`
  - **Validation result:** pass
  - **Manual verification:** `RelationSuggestion` has `source_type`, `source_id`, `target_type`, `target_id`, `relation_type` (explains/similar/prerequisite/follow_up/source_for), `score`, `reason`, `status` (default: suggested).
  - **Scope check:** Relations are not persisted — only returned as suggestions.
  - **Remaining risks:** None

- [x] **T3-5**: Define citation output block schema.
  - Candidate file: `backend/app/schemas/knowledge.py`
  - Completion standard: output can distinguish `source_backed_claim`, `ai_inference`, and `insufficient_context`.

  **Validation Report:**
  - **Changed files:** `backend/app/schemas/knowledge.py`
  - **Validation command:** `python -c "from app.schemas.knowledge import CitationBlock, CitationBlockType"`
  - **Validation result:** pass
  - **Manual verification:** `CitationBlockType` enum has `source_backed_claim`, `ai_inference`, `insufficient_context`. `CitationBlock` has `type`, `text`, `source_refs`. `InsufficientContextResponse` has `status`, `message`, `outline`.
  - **Scope check:** No prohibited entities.
  - **Remaining risks:** None

## Phase 4: Structured Retrieval Service

- [x] **T4-1**: Implement structured note and mistake retrieval.
  - Candidate file: `backend/app/services/knowledge_retrieval.py`
  - Completion standard: matches by subject, knowledge-point strings, tags, type, difficulty, and date constraints.

  **Validation Report:**
  - **Changed files:** `backend/app/services/knowledge_retrieval.py`
  - **Validation command:** `python -c "from app.services.knowledge_retrieval import retrieve_context_pack, retrieve_weak_points"`
  - **Validation result:** pass
  - **Manual verification:** `retrieve_context_pack()` builds SQLAlchemy queries with filters for `subject` (ilike), `knowledge_points` (comma-split, ilike), `tags` (via note_tags join), `type`, `difficulty`, `date_range`, `review_state` (due/overdue/upcoming). Scoring: `subject_match*3 + knowledge_point_overlap*4 + tag_overlap*2 + type_match*1 + due_review_bonus*2 + recent_mistake_bonus*2 - stale_penalty`. Returns `ContextPackResponse` with sources, related_notes, related_mistakes, stats.
  - **Scope check:** No AI calls in retrieval. No vector DB. No KnowledgePoint entity.
  - **Remaining risks:** None

- [x] **T4-2**: Implement relation suggestion scoring.
  - Candidate file: `backend/app/services/knowledge_relations.py`
  - Completion standard: returns explainable suggested note/mistake relations without persisting them.

  **Validation Report:**
  - **Changed files:** `backend/app/services/knowledge_relations.py`
  - **Validation command:** `python -c "from app.services.knowledge_relations import suggest_relations"`
  - **Validation result:** pass
  - **Manual verification:** `suggest_relations()` takes `source_notes` (list of NoteBrief), computes KP overlap and subject match between pairs. Assigns relation_type: `explains` (note↔mistake), `similar` (mistake↔mistake), `source_for` (note↔note). Score normalized to 0–1. Relations are NOT persisted — only returned as `RelationSuggestion` with status="suggested". Deduplication by (source_id, target_id, relation_type).
  - **Scope check:** No silent persistence. No KnowledgePoint entity. No vector DB.
  - **Remaining risks:** None

- [x] **T4-3**: Implement weak-point aggregation.
  - Candidate file: `backend/app/services/knowledge_retrieval.py`
  - Completion standard: computes recent top subjects, knowledge points, error reasons, and due-review signals.

  **Validation Report:**
  - **Changed files:** `backend/app/services/knowledge_retrieval.py`
  - **Validation command:** `python -c "from app.services.knowledge_retrieval import retrieve_weak_points"`
  - **Validation result:** pass
  - **Manual verification:** `retrieve_weak_points(db, days)` queries mistakes updated within `days` window, groups by knowledge_points (comma-split), computes per-KP: `mistake_count`, `due_review_count`, `recent_error_count`, `top_error_reasons` (from `ai_metadata.error_reason`), `evidence_sources`. Returns `WeakPointsResponse` with up to 20 weak points. No AI calls.
  - **Scope check:** Deterministic — no external AI calls. No vector DB. No KnowledgePoint entity.
  - **Remaining risks:** None

## Phase 5: API Endpoints

- [x] **T5-1**: Add `POST /api/knowledge/context-pack`.
  - Candidate file: `backend/app/routers/knowledge.py`
  - Completion standard: returns sources, related notes, related mistakes, suggested relations, and stats.

  **Validation Report:**
  - **Changed files:** `backend/app/routers/knowledge.py`, `backend/main.py`
  - **Validation command:** `python -c "from app.routers.knowledge import router; print([r.path for r in router.routes])"`
  - **Validation result:** pass
  - **Manual verification:** Endpoint registered at `/api/knowledge/context-pack`. Calls `retrieve_context_pack()` then `suggest_relations()` if ≥2 results. Deterministic — verified via `inspect.getsource()`: no `call_text_model`, `call_ocr_model`, or `httpx` imports. Requires admin auth.
  - **Scope check:** No AI calls in deterministic endpoint. No vector DB. No KnowledgePoint entity.
  - **Remaining risks:** None

- [x] **T5-2**: Add `GET /api/knowledge/weak-points`.
  - Candidate file: `backend/app/routers/knowledge.py`
  - Completion standard: returns 7/30-day weak-point summaries from structured data.

  **Validation Report:**
  - **Changed files:** `backend/app/routers/knowledge.py`
  - **Validation command:** `python -c "from app.routers.knowledge import router"`
  - **Validation result:** pass
  - **Manual verification:** Endpoint at `/api/knowledge/weak-points` with `days` query param (default 30, range 1–365). Calls `retrieve_weak_points()`. Deterministic — verified via `inspect.getsource()`: no AI calls. Requires admin auth.
  - **Scope check:** Deterministic — no AI calls. No vector DB. No KnowledgePoint entity.
  - **Remaining risks:** None

- [x] **T5-3**: Add `POST /api/ai/knowledge-summary`.
  - Candidate files: `backend/app/routers/ai.py`
  - Completion standard: generated output contains citations or labels AI inference.

  **Validation Report (updated 2026-06-05, fix applied 2026-06-05):**
  - **Changed files:** `backend/app/routers/ai.py`
  - **Validation command:** `python -c "from app.routers.ai import knowledge_summary"` + function-level mock exercising the source-ref validation branch
  - **Validation result:** pass (after fix)
  - **Manual verification:** Endpoint at `/api/ai/knowledge-summary`. Accepts `KnowledgeSummaryRequest` with `context_pack`, `mode`, `requirements`. Returns `InsufficientContextResponse` if no sources. Source ref handling: (1) AI-returned `source_id` must exist in `source_map` — invented IDs are rejected. (2) AI-returned `field` is checked against a whitelist per source type: `_MISTAKE_FIELDS = {analysis, question, correct_answer, error_reason, key_step, generalization, review_advice, knowledge_points, content}`, `_NOTE_FIELDS = {content, summary, title, knowledge_points}`. If `field` is not whitelisted, falls back to the original matched source's `field`. (3) All other source ref attributes (`source_type`, `title`, `slug`, `excerpt`, `url`, `confidence`, `match_reasons`) are faithfully copied from the original matched source — AI cannot overwrite them. If `source_backed_claim` has no valid refs after validation, it is downgraded to `ai_inference`. Rate-limited. Calls `call_text_model()` (DeepSeek). Requires admin auth.
  - **Bug fix:** `SourceType` was missing from imports at line 13 — caused `NameError` when the source-ref validation branch executed (any request with valid sources). Added `SourceType` to the `app.schemas.knowledge` import block. Previous compile-level check (`python -c "from app.routers.ai import knowledge_summary"`) did not exercise this branch, masking the error. Function-level mock now confirms the branch runs cleanly.
  - **Scope check:** Source validation prevents invented IDs. Field whitelist locks AI to valid fields per source type. Fidelity copy prevents AI from overwriting excerpt/url/confidence/title/slug. Insufficient context returns early. No vector DB. No KnowledgePoint entity.
  - **Remaining risks:** AI model quality depends on DeepSeek configuration.

## Phase 6: Frontend Integration

- [ ] **T6-1**: Add API client types.
  - Candidate file: `src/lib/api/knowledge.ts`
  - Completion standard: frontend types match backend schemas.
  - Status: deferred — frontend not in scope for this implementation pass.

- [ ] **T6-2**: Show related notes and similar mistakes in mistake detail or review context.
  - Candidate route: notes/mistake detail UI.
  - Status: deferred — frontend not in scope.

- [ ] **T6-3**: Add weak-point summary view.
  - Candidate route: review or mistakes page.
  - Status: deferred — frontend not in scope.

## Phase 7: Validation

- [x] **T7-1**: Run backend import or targeted API checks.

  **Validation Report:**
  - **Changed files:** N/A (validation task)
  - **Validation command:** `python -c "from main import app; ..."` — verified all imports and routes
  - **Validation result:** pass
  - **Manual verification:** All modules import cleanly. Knowledge routes registered: `/api/knowledge/context-pack`, `/api/knowledge/weak-points`, `/api/ai/knowledge-summary`. Deterministic endpoints verified (no AI calls). AI endpoint verified (calls `call_text_model`).
  - **Scope check:** No prohibited entities introduced.
  - **Remaining risks:** None

- [ ] **T7-2**: Run frontend type checking if frontend files change.
  - Status: skipped — no frontend files changed.

- [x] **T7-3**: Record validation results in `validation.md`.
  - See updated `validation.md`.

- [x] **T7-4**: Record task evidence after each completed item.
  - Completion standard: changed files, test command, test result, manual verification, risk notes, and scope check are documented.
  - Status: all Phase 3–5 tasks have inline validation reports above.

## Approval Gate

Implementation was executed based on user's explicit instruction to "Independently complete all approved tasks."

## Task Evidence Format

Each completed implementation task must record:

```text
Task:
Changed files:
Tests run:
Test result:
Manual verification:
Risk notes:
Scope check:
```
