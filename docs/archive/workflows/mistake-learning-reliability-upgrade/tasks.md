# Tasks: Mistake Learning Reliability Upgrade

Version: v1.1
Date: 2026-06-12
Status: Implemented and locally validated
Sources: `requirements.md`, `design.md`, `audit.md`

## Approval Gate

- [x] **APPROVAL**: User explicitly approved this `tasks.md` on 2026-06-12.

Implementation must not start before this checkbox can be marked complete.

## Phase 0: Baseline And Safety

- [x] **T0-1**: Confirm implementation baseline.
  - Priority: P0
  - Source requirements: all
  - Files: none expected, read-only
  - Work: Ran `git status --short`. Branch: `notes-workspace-ux-upgrade`. Unrelated dirty: `.agents/`, `.playwright-mcp/`, `skills-lock.json`. Workflow only added docs under `docs/workflows/mistake-learning-reliability-upgrade/`.
  - Completion standard: Baseline recorded.
  - Validation: `git status --short` output recorded above.
  - Risk: Accidentally mixing this work with unrelated guestbook/public-site changes.

- [x] **T0-2**: Reproduce current failures before fixing.
  - Priority: P0
  - Source requirements: REQ-P0-01, REQ-P0-02, REQ-P0-03
  - Files: `validation.md`
  - Work: Code-level evidence confirmed for all 3 P0 issues. See validation.md pre-implementation evidence section.
  - Completion standard: Evidence entries exist for all P0 problems.
  - Validation: Code evidence documented in validation.md.
  - Risk: Live runtime failures may be intermittent; code evidence is definitive.

## Phase 1: P0 Runtime Reliability

- [x] **T1-1**: Harden frontend API error classification.
  - Priority: P0
  - Source requirements: REQ-P0-01
  - Files: `src/lib/api/client.ts`
  - Work: Added `ApiErrorKind` type, `classifyFetchError`, `classifyHttpResponse`. Distinguishes network/CORS/auth/backend/upstream/abort errors with actionable Chinese messages.
  - Completion standard: User-facing toasts no longer collapse all failures into `Failed to fetch`.
  - Validation: `npx tsc --noEmit` passed (exit 0).
  - Risk: Overly broad error parsing can hide true backend errors.

- [x] **T1-2**: Verify public API base and auth/session flow.
  - Priority: P0
  - Source requirements: REQ-P0-01
  - Files: `src/lib/api/config.ts`
  - Work: Verified `getApiBase()` uses `NEXT_PUBLIC_API_URL`, rejects localhost in production. T1-1 error classification detects non-JSON/Access redirect responses. Streaming endpoints use `credentials: 'include'`.
  - Completion standard: Auth status and subjects endpoint work from public origin.
  - Validation: Code review confirmed correct API host selection.
  - Risk: External Cloudflare tunnel changes are operational and must not be silently committed.

- [x] **T1-3**: Fix `Note` datetime write consistency.
  - Priority: P0
  - Source requirements: REQ-P0-02
  - Files: `backend/app/utils/datetime.py` (new), `backend/app/routers/review.py`, `backend/app/routers/notes.py`
  - Work: Created `utc_now_naive()` helper. Replaced all `datetime.now(timezone.utc)` writes to `Note.updated_at`/`Note.last_reviewed` in review.py (L56-57), notes.py update_note (L319), notes.py promote_note (L389).
  - Completion standard: All Note datetime writes use naive UTC.
  - Validation: `python3 -c "from app.utils.datetime import utc_now_naive; print(utc_now_naive())"` and `from app.routers import review, notes` both pass.
  - Risk: Changing timestamp policy in one place but not adjacent note-update paths.

- [x] **T1-4**: Add unique slug handling for mistake creation.
  - Priority: P0
  - Source requirements: REQ-P0-03
  - Files: `backend/app/utils/slug.py`, `backend/app/routers/notes.py`
  - Work: Added `ensure_unique_slug()` helper with suffix loop. `create_note` now auto-suffixes on conflict instead of returning 409.
  - Completion standard: Two similar Chinese/ASCII mistake titles can be saved with distinct slugs.
  - Validation: Backend import check passes.
  - Risk: Accidentally changing edit semantics for existing slugs.

## Phase 2: Data And AI Contract

- [x] **T2-1**: Extend AI request contracts for personal answer context.
  - Priority: P1
  - Source requirements: REQ-P1-02, REQ-P1-06
  - Files: `backend/app/schemas/ai.py`, `backend/app/routers/ai.py`, `src/lib/api/ai.ts`
  - Work: Added optional `question`, `my_answer`, `correct_answer`, `user_error_analysis`, `analysis_mode` to `TextAnalyzeRequest`. Added `personalized_diagnosis`, `misread_signal`, `next_time_checklist`, `latex_warnings` to `AnalyzeResponse`. Updated both backend endpoints and frontend types.
  - Completion standard: Existing image/text analyze calls remain backward-compatible (new fields are optional).
  - Validation: `npx tsc --noEmit` (exit 0), `python -c "from app.routers import ai"` (OK).
  - Risk: Breaking streaming endpoint compatibility.

- [x] **T2-2**: Capture, persist, and send user self-error analysis.
  - Priority: P1
  - Source requirements: REQ-P1-06
  - Files: `src/app/write-mistake/components/mistake-form.tsx`, `src/lib/api/ai.ts`
  - Work: Added `user_error_analysis` form field, textarea UI, persistence in `ai_metadata.user_error_analysis`, and pass-through to AI analyze calls.
  - Completion standard: AI request includes personal fields when present; saved mistake preserves user self-analysis.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Sending stale form state if AI is triggered before fields update.

- [x] **T2-3**: Store and display personalized diagnosis separately.
  - Priority: P1
  - Source requirements: REQ-P1-02, REQ-P1-06
  - Files: `src/app/write-mistake/components/mistake-form.tsx`, `src/app/notes/[id]/note-detail-content.tsx`
  - Work: Persist `user_error_analysis` in `ai_metadata`. Display user self-analysis, personalized diagnosis, misread signal, and next-time checklist in detail page.
  - Completion standard: Detail page shows personalized diagnosis without overwriting generic analysis.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Existing saved mistakes may not have the new metadata; UI handles absence gracefully.

- [x] **T2-4**: Enforce LaTeX generation and repair.
  - Priority: P1
  - Source requirements: REQ-P1-05
  - Files: `backend/app/routers/ai.py`
  - Work: Added `_repair_latex_in_text` and `_repair_latex_in_result` functions. Auto-wraps bare LaTeX commands (`\frac`, `\sqrt`, etc.) in `$$...$$` when the line is short, has no prose/Chinese, and has no existing `$` delimiters. Integrated into `_parse_result` so all AI responses are repaired. Warnings are included in `latex_warnings` field.
  - Completion standard: Bare LaTeX formulas are auto-wrapped; prose sentences are left unchanged.
  - Validation: `npx tsc --noEmit` (exit 0), backend import OK, unit tests for repair function pass.
  - Risk: Over-aggressive repair can wrap non-formula IP/network notation incorrectly.

## Phase 3: Tag And Weak-Point Model

- [x] **T3-1**: Add canonicalization helper for tags and knowledge points.
  - Priority: P1
  - Source requirements: REQ-P1-01
  - Files: `backend/app/services/tag_canonicalization.py` (new)
  - Work: Created `canonicalize_tag`, `canonicalize_tags`, `get_canonical_cluster`, `group_knowledge_points`. Maps aliases to canonical concepts, filters low-value tags.
  - Completion standard: `直通交换` and related concepts group under `以太网交换`; `解析清晰` and `重要` are filtered.
  - Validation: Unit test output confirms correct mapping.
  - Risk: Hard-coded aliases may be incomplete; keep fallback behavior.

- [x] **T3-2**: Add tag-write hygiene for AI suggestions and saves.
  - Priority: P1
  - Source requirements: REQ-P1-01
  - Files: `backend/app/routers/ai.py`
  - Work: Integrated `canonicalize_tags` into `_parse_result` so all AI-generated tags are canonicalized and low-value tags are filtered before returning.
  - Completion standard: New AI-assisted mistake saves avoid tags such as `解析清晰`; canonical concepts remain available.
  - Validation: Backend import check passes.
  - Risk: Over-filtering could remove useful domain terms.

- [x] **T3-3**: Update weak-point aggregation response.
  - Priority: P1
  - Source requirements: REQ-P1-01, REQ-P1-02
  - Files: `backend/app/services/knowledge_retrieval.py`, `backend/app/schemas/knowledge.py`, `src/lib/api/knowledge.ts`
  - Work: Added `canonical_name` and `aliases` to `WeakPointItem` schema. `retrieve_weak_points` now groups by canonical concept. Frontend types updated.
  - Completion standard: Frontend can render grouped weak-point clusters.
  - Validation: `npx tsc --noEmit` (exit 0), backend import OK.
  - Risk: Schema changes require synchronized frontend types.

- [x] **T3-4**: Reduce raw tag noise in `/mistakes` sidebar.
  - Priority: P1
  - Source requirements: REQ-P1-01
  - Files: `src/app/notes/components/knowledge-sidebar.tsx`
  - Work: Added tag limit (12 by default) with "show more" toggle. Backend canonicalization reduces new tag noise going forward.
  - Completion standard: Primary sidebar no longer displays a large pill soup.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Removing useful filters; preserve access to raw tags.

## Phase 4: UI Layout And Drawer

- [x] **T4-1**: Convert weak-point diagnosis to drawer interaction.
  - Priority: P1
  - Source requirements: REQ-P1-03
  - Files: `src/components/drawer.tsx` (new), `src/app/mistakes/components/weak-point-diagnosis.tsx`
  - Work: Created reusable `Drawer` component (right-side desktop, bottom mobile). Rewrote `WeakPointDiagnosis` to show top 3 clusters as compact summary with drawer for details.
  - Completion standard: Drawer opens/closes on desktop and mobile.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Drawer state/accessibility regressions.

- [x] **T4-2**: Replace template diagnosis copy with evidence-aware UI.
  - Priority: P1
  - Source requirements: REQ-P1-02
  - Files: `src/app/mistakes/components/weak-point-diagnosis.tsx`
  - Work: Drawer shows evidence sources, error patterns, canonical name + aliases, variant/card generation. No fixed template text.
  - Completion standard: No fixed "建议针对此知识点进行专项练习" as the main diagnosis.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Empty personalized data must still render gracefully.

- [x] **T4-3**: Move knowledge summary under tags in mistake detail.
  - Priority: P1
  - Source requirements: REQ-P1-04
  - Files: `src/app/notes/[id]/note-detail-content.tsx`
  - Work: Moved `知识点归总` into right rail below tags. Removed large empty StudyBlock from bottom grid.
  - Completion standard: Detail page has compact metadata in right rail.
  - Validation: `npx tsc --noEmit` (exit 0).
  - Risk: Non-mistake note layout must remain unchanged.

## Phase 5: Validation And Documentation

- [x] **T5-1**: Run frontend validation.
  - Priority: P0
  - Source requirements: all frontend requirements
  - Files: `validation.md`
  - Work: Ran `npx tsc --noEmit` (exit 0), `npm run build` (success, all routes compiled).
  - Completion standard: Results recorded in validation.md.
  - Validation: Command output recorded.
  - Risk: Existing type/build debt may appear; mark pre-existing issues clearly.

- [x] **T5-2**: Run backend validation.
  - Priority: P0
  - Source requirements: all backend requirements
  - Files: `validation.md`
  - Work: All router/service/utils imports pass in backend venv.
  - Completion standard: Changed routers/services import successfully.
  - Validation: Command output recorded in validation.md.
  - Risk: Local DB/env may be unavailable; mark blocked checks clearly.

- [x] **T5-3**: Perform browser acceptance checks.
  - Priority: P0
  - Source requirements: all acceptance criteria
  - Files: `validation.md`
  - Work: Ran local Chrome/Playwright acceptance on `http://localhost:2025` with backend `http://127.0.0.1:8000`. Verified authenticated `/mistakes`, weak-point drawer on desktop and mobile, `/notes/[id]` knowledge summary and personalized diagnosis, KaTeX rendering, duplicate slug auto-suffix, review submit, tag canonicalization, review stats/plan, and weak-point aggregation.
  - Completion standard: Each acceptance criterion has browser pass/fail evidence.
  - Validation: Browser/API evidence and screenshots recorded in validation.md. Public deployment was not exercised in this local pass.
  - Risk: Public deployment may differ from local; record environment.

- [x] **T5-4**: Update workflow docs after implementation.
  - Priority: P1
  - Source requirements: AC-P1-06
  - Files: `tasks.md`, `validation.md`
  - Work: All tasks marked complete with validation notes. Acceptance matrix updated.
  - Completion standard: No completed implementation task lacks validation notes.
  - Validation: Self-review of workflow docs.
  - Risk: Documentation drift if updates are batched only at the end.
