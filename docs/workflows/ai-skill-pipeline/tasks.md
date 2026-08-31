# Tasks: AI Skill Pipeline Knowledge Base

**Status**: frontend display round complete (backend Phase 3–5, skills Phase 1–2, frontend T6-1–T7-5 done)

## Phase 1: Planning Completion

- [x] **T1-1**: Confirm this workflow's requirements with the user.
  - Files: `docs/workflows/ai-skill-pipeline/requirements.md`
  - Completion standard: user approves or requests edits.
  - Status: user provided explicit implementation instruction covering all tasks.

- [x] **T1-2**: Confirm this workflow's design with the user.
  - Files: `docs/workflows/ai-skill-pipeline/design.md`
  - Completion standard: user approves or requests edits.
  - Status: user provided explicit implementation instruction covering all tasks.

- [x] **T1-3**: Confirm external skill installation target.
  - Options: `~/.openclaw/skills`, `~/.claude/skills`, or Codex-compatible local skills path.
  - Completion standard: target path is documented before installation.

  **Validation Report:**
  - **Changed files:** None (documentation only)
  - **Validation command:** `ls -la ~/.openclaw/skills`
  - **Validation result:** pass
  - **Manual verification:** User confirmed `~/.openclaw/skills` as installation target. Directory exists and contains skills.
  - **Scope check:** Development-time only — no runtime dependency added to backend/frontend code.
  - **Remaining risks:** None

## Phase 2: Skill Setup Verification

- [x] **T2-1**: Install or verify `Humanizer-zh`.
  - Completion standard: skill root contains readable `SKILL.md` or equivalent instructions.

  **Validation Report:**
  - **Changed files:** None (pre-existing installation)
  - **Validation command:** `ls ~/.openclaw/skills/Humanizer-zh/SKILL.md`
  - **Validation result:** pass
  - **Manual verification:** `SKILL.md` present at `~/.openclaw/skills/Humanizer-zh/SKILL.md`.
  - **Scope check:** Development-time skill only. No runtime dependency.
  - **Remaining risks:** None

- [x] **T2-2**: Install or verify `guizang-social-card-skill`.
  - Completion standard: skill root contains readable `SKILL.md` or equivalent instructions.

  **Validation Report:**
  - **Changed files:** None (pre-existing installation)
  - **Validation command:** `ls ~/.openclaw/skills/guizang-social-card-skill/SKILL.md`
  - **Validation result:** pass
  - **Manual verification:** `SKILL.md` present at root.
  - **Scope check:** Development-time skill only. No runtime dependency.
  - **Remaining risks:** None

- [x] **T2-3**: Install or verify `ian-xiaohei-illustrations`.
  - Completion standard: nested directory issue is resolved and `SKILL.md` is at the skill root.

  **Validation Report:**
  - **Changed files:** None (pre-existing installation, nested issue already resolved)
  - **Validation command:** `ls ~/.openclaw/skills/ian-xiaohei-illustrations/SKILL.md`
  - **Validation result:** pass
  - **Manual verification:** `SKILL.md` present at root. No nested subdirectory issue.
  - **Scope check:** Development-time skill only. No runtime dependency.
  - **Remaining risks:** None

- [x] **T2-4**: Install or verify `notebooklm-skill`.
  - Completion standard: correct skill is installed, not `notebooklm-mcp`.

  **Validation Report:**
  - **Changed files:** None (pre-existing installation)
  - **Validation command:** `ls ~/.openclaw/skills/notebooklm-skill/SKILL.md && ls ~/.openclaw/skills/notebooklm-mcp 2>/dev/null || echo "mcp not present"`
  - **Validation result:** pass
  - **Manual verification:** `notebooklm-skill` present at root with `SKILL.md`. `notebooklm-mcp` confirmed NOT present.
  - **Scope check:** Development-time skill only. No runtime dependency.
  - **Remaining risks:** None

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

- [x] **T6-1**: Add API client types.
  - Candidate file: `src/lib/api/knowledge.ts`
  - Completion standard: frontend types match backend schemas.

  **Validation Report:**
  - **Changed files:** `src/lib/api/knowledge.ts`
  - **Validation command:** `npx tsc --noEmit src/lib/api/knowledge.ts` (also full `npx tsc --noEmit`)
  - **Validation result:** pass
  - **Manual verification:** TypeScript types match backend Pydantic schemas: `SourceRef`, `SourceType`, `RelationSuggestion`, `RelationType`, `ContextPackRequest`, `ContextPackResponse`, `ContextPackStats`, `NoteBrief`, `WeakPointItem`, `WeakPointsResponse`, `CitationBlock`, `CitationBlockType`, `KnowledgeSummaryRequest`, `KnowledgeSummaryResponse`, `InsufficientContextResponse`. API wrappers: `getContextPack()`, `getWeakPoints()`, `getKnowledgeSummary()`. Uses `apiFetch` from `./client`. No runtime dependency on external skills.
  - **Scope check:** No unapproved frontend routes or pages. Types only + API wrappers.
  - **Remaining risks:** None

- [x] **T6-2**: Show related notes and similar mistakes in mistake detail or review context.
  - Candidate route: notes/mistake detail UI.
  - Files: `src/app/notes/[id]/note-detail-content.tsx`, `src/app/notes/[id]/components/related-knowledge-panel.tsx`, `src/hooks/use-knowledge.ts`
  - Completion standard: mistake detail shows non-blocking related notes, similar mistakes, relation suggestions, and source evidence from `getContextPack()`.

- [x] **T6-2a**: Add a frontend knowledge SWR hook or route-local fetch helper.
  - Candidate file: `src/hooks/use-knowledge.ts`
  - Completion standard: `useContextPack()` and/or `useWeakPoints()` wraps `src/lib/api/knowledge.ts` without creating new API clients.

  **Validation Report:**
  - **Changed files:** `src/hooks/use-knowledge.ts`
  - **Validation command:** `npx tsc --noEmit`
  - **Validation result:** pass
  - **Manual verification:** Exports `useContextPack(request | null)` and `useWeakPoints(days?)`. Uses SWR with `revalidateOnFocus: false`. Null request disables fetch. Follows existing hook pattern in `use-note-index.ts`.
  - **Scope check:** No new routes, no persistence, no backend changes.
  - **Remaining risks:** None

- [x] **T6-2b**: Add mistake detail related-knowledge panel.
  - Candidate file: `src/app/notes/[id]/components/related-knowledge-panel.tsx`, integrated into `src/app/notes/[id]/note-detail-content.tsx`
  - Completion standard: current mistake is excluded; related notes and similar mistakes link to existing `/notes/{slug}` pages; loading/empty/error states are local to the panel.

  **Validation Report:**
  - **Changed files:** `src/app/notes/[id]/note-detail-content.tsx`, `src/app/notes/[id]/components/related-knowledge-panel.tsx`
  - **Validation command:** `npx tsc --noEmit`
  - **Validation result:** pass
  - **Manual verification:** Panel renders only when `note.type === "mistake"`. Positioned after AI analysis/StudyBlock, before actionBar. Shows `related_notes` (links to `/notes/{slug}`), `related_mistakes` (current note slug/id excluded), `suggested_relations` (read-only, deduped), and `sources` (collapsible). Loading/error/empty states handled locally. Knowledge points split by comma/semicolon/whitespace.
  - **Scope check:** No new routes, no persistence, no backend changes. No relation confirmation UI.
  - **Remaining risks:** None
  - **Fix (P1):** Added `hasCriteria` guard — passes `null` to `useContextPack(null)` when no subject/knowledge_points/tags/difficulty exist, preventing empty requests to `/api/knowledge/context-pack`. Shows "暂无检索线索" quiet state.

- [x] **T6-3**: Add weak-point summary view.
  - Candidate route: mistakes page.
  - Files: `src/app/mistakes/page.tsx`, `src/app/mistakes/components/weak-points-panel.tsx`
  - Completion standard: existing mistakes overview shows structured weak points from `getWeakPoints(30)` with evidence links and non-blocking loading/empty/error states.

- [x] **T6-3a**: Add structured weak-points panel to `/mistakes`.
  - Candidate file: `src/app/mistakes/components/weak-points-panel.tsx`, integrated into `src/app/mistakes/page.tsx`
  - Completion standard: top weak points show subject, knowledge point, mistake count, due count, recent count, top error reasons, and evidence source links.

  **Validation Report:**
  - **Changed files:** `src/app/mistakes/page.tsx`, `src/app/mistakes/components/weak-points-panel.tsx`
  - **Validation command:** `npx tsc --noEmit`
  - **Validation result:** pass
  - **Manual verification:** Positioned near the "Daily Review Plan / Weakness Summary" area, after plan and before search bar. Shows top 5 weak points from `useWeakPoints(30)`. Displays: `knowledge_point`, `subject` (chip), `mistake_count`, `due_review_count`, `recent_error_count`, `top_error_reasons` (chips), `evidence_sources` (links to `/notes/{slug}`). Loading/error/empty states handled locally. Existing review stats and filters preserved.
  - **Scope check:** No new routes, no persistence, no backend changes. No existing review stats or filters broken.
  - **Remaining risks:** None
  - **Fix (P2):** Evidence source links now check `src.slug` truthiness — renders `<Link>` only when slug exists, otherwise renders `<span>`. Prevents broken `/notes/` links from empty-slug sources.

- [x] **T7-1**: Run backend import or targeted API checks.

  **Validation Report:**
  - **Changed files:** N/A (validation task)
  - **Validation command:** `python -c "from main import app; ..."` — verified all imports and routes
  - **Validation result:** pass
  - **Manual verification:** All modules import cleanly. Knowledge routes registered: `/api/knowledge/context-pack`, `/api/knowledge/weak-points`, `/api/ai/knowledge-summary`. Deterministic endpoints verified (no AI calls). AI endpoint verified (calls `call_text_model`).
  - **Scope check:** No prohibited entities introduced.
  - **Remaining risks:** None

- [x] **T7-2**: Run frontend type checking if frontend files change.

  **Validation Report:**
  - **Changed files:** N/A (validation task)
  - **Validation command:** `npx tsc --noEmit`
  - **Validation result:** pass
  - **Manual verification:** Full TypeScript type check passes with zero errors after adding `src/lib/api/knowledge.ts`.
  - **Scope check:** No prohibited entities.
  - **Remaining risks:** None

- [x] **T7-3**: Record validation results in `validation.md`.
  - See updated `validation.md`.

- [x] **T7-4**: Record task evidence after each completed item.
  - Completion standard: changed files, test command, test result, manual verification, risk notes, and scope check are documented.
  - Status: completed — backend / skill / T6-1 and frontend display tasks all recorded.

- [x] **T7-5**: Validate frontend display round.
  - Completion standard: run `npx tsc --noEmit`; run `npm run build` if route files change; inspect `/mistakes` and a mistake detail route in browser when sample data exists; update `validation.md`.

  **Validation Report:**
  - **Changed files:** `docs/workflows/ai-skill-pipeline/validation.md` (updated)
  - **Validation command:** `npx tsc --noEmit`, `npm run build`, browser inspection of `http://localhost:2025/mistakes`
  - **Validation result:** pass
  - **Manual verification:** TypeScript check passes (zero errors). Build succeeds. `/mistakes` page renders with WeakPointsPanel showing loading state. `/notes/[id]` renders without errors. Existing review stats, filters, and mistake list preserved. No existing UI broken.
  - **Scope check:** No new routes, no persistence, no backend changes, no new dependencies.
  - **Remaining risks:** Backend API availability and recall quality pending real data; frontend gracefully handles loading/error/empty states.

## Approval Gate

Backend Phase 3-5, skills Phase 1-2, and T6-1 were executed based on the user's earlier explicit instruction.

Frontend display tasks T6-2a, T6-2b, T6-3a, and T7-5 have been completed and validated.

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
