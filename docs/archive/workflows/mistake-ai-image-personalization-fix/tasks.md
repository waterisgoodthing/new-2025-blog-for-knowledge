# Tasks: AI Mistake And Prompt Management Upgrade

Version: v0.2
Date: 2026-06-14
Status: Final validation completed. Provider routing, image-only AI acceptance, local browser checks, and music diagnostics/generation failure classification are recorded in `validation.md`. Music remains data-blocked by empty candidate pool / unreachable NetEase API, not by frontend API origin.
Sources: `audit.md`, `requirements.md`, `design.md`

## Approval Gate

- [x] **APPROVAL**: User explicitly approved this `tasks.md` in conversation (via /goal instruction 2026-06-14T17:20+08:00).

Implementation must not start before this checkbox can be marked complete.

## Phase 0: Baseline, Reproduction, And Model Verification

- [x] **T0-1**: Record baseline.
  - Priority: P0
  - Domains: `mistakes`, `notes`, `manage`, `backend`, shared infrastructure
  - Files: `validation.md`
  - Work: Record `git status --short`, current branch, and unrelated dirty files before implementation.
  - Completion standard: Baseline evidence is written to `validation.md`.

- [x] **T0-2**: Reproduce or confirm the `/write-mistake` Mermaid syntax overlay.
  - Priority: P0
  - Domains: `mistakes`, shared infrastructure
  - Files: `validation.md`, optionally `assets/`
  - Work: Open `/write-mistake`, capture browser-visible evidence if the overlay appears, and check console if available.
  - Completion standard: The overlay is either reproduced with evidence or marked not reproduced with environment details.

- [x] **T0-3**: Record Qwen3.7 Plus official/runtime evidence.
  - Priority: P0
  - Requirements: REQ-07
  - Files: `validation.md`
  - Work: Record official model ID evidence and local runtime test for `qwen3.7-plus`.
  - Completion standard: `validation.md` clearly states the callable model ID and whether current credentials can use it.

## Phase 1: Backend Model Routing

- [x] **T1-1**: Change general AI default to Qwen3.7 Plus.
  - Priority: P0
  - Requirements: REQ-07
  - Files: `backend/app/config.py`, `backend/.env.example`
  - Work: Default `AI_MODEL` to `qwen3.7-plus`, update `.env.example`, and align effective runtime behavior with DashScope when `AI_API_KEY` is empty but `DASHSCOPE_API_KEY` is configured.
  - Completion standard: `/api/ai/config` and a direct `get_settings()` runtime check report the effective general route as Qwen/DashScope rather than `gpt-4o`/OpenAI unless the user explicitly overrides it.

- [x] **T1-2**: Add provider registry and route-aware JSON calls.
  - Priority: P0
  - Requirements: REQ-08
  - Files: `backend/app/services/ai_service.py`
  - Work: Implement provider descriptors, attempt metadata, fallback order, and JSON model calls.
  - Completion standard: `call_text_model()` and `call_ocr_model()` still work but can fall back to `qwen3.7-plus`.

- [x] **T1-3**: Add route-aware streaming calls for polish.
  - Priority: P0
  - Requirements: REQ-08, REQ-09
  - Files: `backend/app/services/ai_service.py`, `backend/app/services/ai_polish_service.py`
  - Work: Move streaming provider selection into shared service or equivalent helper; support fallback for polish streaming.
  - Completion standard: `/api/ai/polish` can use DeepSeek primary and Qwen fallback.

- [x] **T1-4**: Update recommendation AI calls to use general Qwen route.
  - Priority: P1
  - Requirements: REQ-07, REQ-08
  - Files: `backend/app/services/recommendation.py`
  - Work: Replace direct `AI_API_KEY`-only call with route-aware general AI call.
  - Completion standard: daily recommendation can work with DashScope/Qwen configuration.

## Phase 2: Learner Context UX

- [x] **T2-1**: Rename user-facing wrong-answer copy to wrong-thought copy.
  - Priority: P0
  - Requirements: REQ-01, REQ-02
  - Files: `src/app/write-mistake/components/mistake-form.tsx`
  - Work: Update placeholders/headings/generated content labels from "我的错误答案" toward "我的错误思路 / 当时答案" while preserving the `my_answer` field.
  - Completion standard: The form and saved markdown no longer center only the final wrong answer.

- [x] **T2-2**: Make personal context visible before AI generation.
  - Priority: P0
  - Requirements: REQ-01
  - Files: `src/app/write-mistake/components/mistake-form.tsx`
  - Work: Reorder or reframe the form so wrong thought and self-identified error point are naturally entered before AI buttons, or add an explicit generic-analysis warning when both are empty.
  - Completion standard: Upload/text AI calls are clearly personalized only when context exists.

- [x] **T2-3**: Store personal diagnosis metadata consistently.
  - Priority: P1
  - Requirements: REQ-01, REQ-02
  - Files: `src/app/write-mistake/components/mistake-form.tsx`
  - Work: Ensure `user_error_analysis`, `personalized_diagnosis`, `misread_signal`, and `next_time_checklist` stay in `ai_metadata` without overwriting manual fields.
  - Completion standard: Existing edit flow keeps old metadata and new records persist the entered self-analysis.

## Phase 3: Image Analysis And Visual Context

- [x] **T3-1**: Extend AI response contracts for visual context.
  - Priority: P0
  - Requirements: REQ-02, REQ-04
  - Files: `backend/app/schemas/ai.py`, `src/lib/api/ai.ts`
  - Work: Add optional `visual_context` and `image_dependency` fields to backend/frontend response types.
  - Completion standard: Type contracts compile and remain backward-compatible.

- [x] **T3-2**: Update image-analysis prompt to solve when possible.
  - Priority: P0
  - Requirements: REQ-03, REQ-04, REQ-05
  - Files: `backend/app/routers/ai.py`
  - Work: Modify image prompt so clear question images can generate answer and explanation, while preserving OCR uncertainty and forbidding final-reasoning hedge words.
  - Completion standard: The prompt no longer instructs the model to avoid complete solving for the write-mistake use case.

- [x] **T3-3**: Centralize personal-context prompt construction.
  - Priority: P1
  - Requirements: REQ-01, REQ-03
  - Files: `backend/app/routers/ai.py`
  - Work: Replace duplicated personal-context string construction across sync/stream text/image endpoints with a helper.
  - Completion standard: All four analysis endpoints use equivalent personal-context instructions.

- [x] **T3-4**: Persist and display visual context.
  - Priority: P1
  - Requirements: REQ-04
  - Files: `src/app/write-mistake/components/mistake-form.tsx`, `src/app/notes/[id]/note-detail-content.tsx`
  - Work: Persist `visual_context` and `image_dependency` in `ai_metadata`, then render a compact visual-context section on mistake detail when present.
  - Completion standard: Image-dependent records show original uploaded images and AI visual-context summary near the study content.

- [x] **T3-5**: Add deterministic-analysis guard for AI output.
  - Priority: P0
  - Requirements: REQ-05
  - Files: `backend/app/routers/ai.py`
  - Work: Add a narrow validation/repair step that rejects or regenerates final analysis containing hedge words in answer/derivation fields, while still allowing uncertainty in explicit OCR/missing-info notes.
  - Completion standard: AI output cannot save a final explanation like "可能因偏移单位..." as if it were a valid derivation.

## Phase 4: Mermaid Error Containment

- [x] **T4-1**: Harden `MermaidBlock` render failure behavior.
  - Priority: P0
  - Requirements: REQ-06
  - Files: `src/components/mermaid-block.tsx`
  - Work: Prevent Mermaid parser error graphics from leaking into the page; render a compact safe fallback on invalid syntax.
  - Completion standard: Invalid Mermaid input cannot create a large syntax-error overlay outside the diagram block.

- [x] **T4-2**: Drop or quarantine invalid AI diagrams before detail rendering.
  - Priority: P1
  - Requirements: REQ-06
  - Files: `backend/app/routers/ai.py`, optionally `src/app/notes/[id]/note-detail-content.tsx`
  - Work: Add minimal validation/normalization so empty or obviously non-Mermaid diagram strings are not treated as renderable diagrams.
  - Completion standard: AI metadata does not persist unusable diagram blocks when they can be detected cheaply.

## Phase 5: Prompt Registry And AI Management UI

- [x] **T5-1**: Add prompt registry.
  - Priority: P0
  - Requirements: REQ-09, REQ-10
  - Files: `backend/app/services/ai_prompt_registry.py` or equivalent, related schemas
  - Work: Expose named prompt templates for mistake analysis, polish, tags, knowledge summary, recommendation, and variant/card generation.
  - Completion standard: Backend can return prompt groups without exposing secrets.

- [x] **T5-2**: Add AI management status and prompt test endpoints.
  - Priority: P0
  - Requirements: REQ-08, REQ-09, REQ-10
  - Files: `backend/app/routers/ai.py`, backend schemas
  - Work: Extend AI admin endpoints with provider status, route roles, prompt templates, and an admin-only prompt test endpoint.
  - Completion standard: Prompt tests return provider used, fallback trail, latency, output, and error details.

- [x] **T5-3**: Replace static AI tab with provider status cards.
  - Priority: P0
  - Requirements: REQ-07, REQ-09
  - Files: `src/app/manage/ai-tab.tsx`, optionally `src/lib/api/ai-admin.ts`
  - Work: Render Qwen3.7 Plus, DeepSeek, and DashScope provider cards with model, role, configured state, and last test result.
  - Completion standard: UI no longer shows general AI as unconfigured when Qwen credentials are available.

- [x] **T5-4**: Build visual prompt workspace.
  - Priority: P0
  - Requirements: REQ-09, REQ-10
  - Files: `src/app/manage/ai-tab.tsx`, optional route-specific components
  - Work: Add grouped prompt list, prompt editor, reset draft action, sample input editor, route selector, and result panel.
  - Completion standard: Admin can edit a draft prompt and run a test from `/manage?tab=ai`.

- [x] **T5-5**: Show fallback details in test results.
  - Priority: P1
  - Requirements: REQ-08, REQ-09
  - Files: `src/app/manage/ai-tab.tsx`
  - Work: Render provider used, fallback status, latency, and error trail.
  - Completion standard: A failed primary plus fallback success is visible and understandable.

## Phase 6: Daily Music Generation And Admin Recovery

- [x] **T6-1**: Fix manage music generate action API origin.
  - Priority: P0
  - Requirements: REQ-12
  - Files: `src/app/manage/music-tab.tsx`, existing music API client if needed
  - Work: Replace direct `fetch('/api/music/manage/generate-song')` with the existing typed API wrapper such as `generateDailySong()` / `apiFetch()`.
  - Completion standard: Production manage action targets `NEXT_PUBLIC_API_URL` / `public-api.limengyang.me`, not `blog.limengyang.me/api/...`.

- [x] **T6-2**: Add or expose daily music diagnostics.
  - Priority: P0
  - Requirements: REQ-11
  - Files: backend music router/service, `src/app/manage/music-tab.tsx`
  - Work: Surface daily song existence, history count, candidate pool count, NetEase API configured/reachable status, and last generation/sync result where available.
  - Completion standard: Admin can distinguish public API health from missing daily-song data and empty candidate pool.

- [x] **T6-3**: Define and implement an explicit generation/backfill path.
  - Priority: P1
  - Requirements: REQ-11
  - Files: backend music router/service, optionally manage music UI
  - Work: Ensure manual admin generation gives actionable success/failure responses; add scheduler/cron only if it stays within approved scope and can be validated.
  - Completion standard: Empty candidate pool, NetEase failure, and successful generated song are distinguishable outcomes.

- [x] **T6-4**: Validate public music evidence after repair.
  - Priority: P1
  - Requirements: REQ-11, REQ-12
  - Files: `validation.md`
  - Work: Re-check `/api/health`, `/api/music/manage/daily-song/public`, `/api/music/manage/history/public?limit=30`, and the manage generation action.
  - Completion standard: Validation records whether daily data exists or which owning layer still blocks it.

## Phase 7: Validation And Closure

- [x] **T7-1**: Run frontend validation.
  - Priority: P0
  - Requirements: all frontend requirements
  - Files: `validation.md`
  - Work: Run `npx tsc --noEmit`; run `npm run build` if touched route/rendering code requires it.
  - Completion standard: Results and first relevant failure, if any, are recorded.

- [x] **T7-2**: Run backend validation.
  - Priority: P0
  - Requirements: backend/API requirements
  - Files: `validation.md`
  - Work: Run import checks for AI services/routers and direct runtime calls for Qwen general, text route, and OCR route.
  - Completion standard: Results are recorded.

- [x] **T7-3**: Browser-check `/write-mistake`.
  - Priority: P0
  - Requirements: REQ-01, REQ-06
  - Files: `validation.md`, optionally `assets/`
  - Work: Inspect `/write-mistake` in a browser; confirm no Mermaid syntax overlay and that personal-context UX is visible.
  - Completion standard: Browser evidence is recorded.

- [x] **T7-4**: Image-only AI acceptance check.
  - Priority: P1
  - Requirements: REQ-03, REQ-04, REQ-05
  - Files: `validation.md`
  - Work: Test an uploaded question image without visible answer/analysis if credentials and runtime permit; include a sample that would previously invite "可能" wording.
  - Completion standard: The result is recorded as pass/fail/limited with exact reason.

- [x] **T7-5**: Browser-check `/manage?tab=ai`.
  - Priority: P0
  - Requirements: REQ-07, REQ-08, REQ-09
  - Files: `validation.md`, optionally `assets/`
  - Work: Inspect AI management UI in browser and run at least one prompt test.
  - Completion standard: Browser evidence records provider cards, prompt editor, test result, and no layout overlap.

- [x] **T7-6**: Browser-check music management and public music state.
  - Priority: P1
  - Requirements: REQ-11, REQ-12
  - Files: `validation.md`, optionally `assets/`
  - Work: Inspect `/manage?tab=music` or the owning music management UI and public `/music` state if available.
  - Completion standard: Browser/API evidence records whether daily song generation is repaired or the remaining owner.

- [x] **T7-7**: Update workflow closure docs.
  - Priority: P1
  - Requirements: all
  - Files: `tasks.md`, `validation.md`, `diff-report.md`
  - Work: Mark completed tasks immediately after each item and record validation evidence.
  - Completion standard: No completed task lacks validation notes.
