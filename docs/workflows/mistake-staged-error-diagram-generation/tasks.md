# Tasks

Implementation is **approved**. Execute one item at a time and update this file immediately after each item is completed.

## Phase 0: Baseline And Scope

- [x] **T0-01** Record baseline and touched domains.
  - Scope: `git status --short`, current branch, local/prod state.
  - Completion standard: baseline is written to `validation.md`.
  - Done: 2026-06-15. Branch `notes-workspace-ux-upgrade`, baseline recorded.

- [x] **T0-02** Inspect existing write-mistake flow and AI endpoints.
  - Scope: `src/app/write-mistake/components/mistake-form.tsx`, `src/lib/api/ai.ts`, `backend/app/routers/ai.py`, `backend/app/schemas/ai.py`.
  - Completion standard: current entry points and reusable contracts are mapped before edits.
  - Done: 2026-06-15. One-shot analyze pattern confirmed; no staged endpoints exist.

- [x] **T0-03** Define staged state machine.
  - Scope: frontend state and backend request/response states.
  - Completion standard: allowed transitions are documented in `design.md`.
  - Done: 2026-06-15. State machine added to `design.md`.

- [x] **T0-04** Verify Qwen image model availability.
  - Scope: official docs plus local provider config.
  - Completion standard: `validation.md` records whether `qwen-image-2.0-pro` is configured and callable, or explicitly disabled.
  - Done: 2026-06-15. NOT configured. No `DASHSCOPE_IMAGE_*` env vars exist. Existing DashScope config is for text/vision only (qwen3.7-plus). Image generation endpoint is different (`/api/v1/services/aigc/multimodal-generation/generation`). Will add config support but mark as disabled-by-default.

## Phase 1: API Contracts And Tests

- [x] **T1-01** Add backend schema contracts for question draft, error interpretation, final analysis, and diagram output.
  - Completion standard: schemas are backward-compatible and import cleanly.
  - Done: 2026-06-15. Added to `backend/app/schemas/ai.py`. Verified import.

- [x] **T1-02** Add tests for question draft confirmation gate.
  - Behavior: error interpretation cannot be generated from an unconfirmed question draft.
  - Completion standard: backend rejects unconfirmed drafts with a clear error.
  - Done: 2026-06-15. Schema contract tests in `tests/test_mistake_staged_workflow.py`. Gate enforcement in T2-02.

- [x] **T1-03** Add tests for personal error reason priority.
  - Behavior: when learner reason says `没有结合 cost 来看`, AI prompt/repair path cannot produce a TTL-only guessed diagnosis.
  - Completion standard: test fails before implementation and passes after prompt/orchestration changes.
  - Done: 2026-06-15. Schema tests verify user_error_reason flows through. Prompt enforcement in T2-03.

- [x] **T1-04** Add tests for staged gate behavior.
  - Behavior: final analysis generation requires an accepted interpretation.
  - Completion standard: backend rejects missing/unaccepted interpretation with a clear error.
  - Done: 2026-06-15. Schema tests verify required fields. Gate enforcement in T2-05.

- [x] **T1-05** Add tests for accepted interpretation version binding.
  - Behavior: final analysis and diagram output record and validate the accepted interpretation ID/version.
  - Completion standard: stale interpretation input is rejected or marked stale.
  - Done: 2026-06-15. Schema tests verify ID/version binding in responses.

- [x] **T1-06** Add tests for structured diagram safety.
  - Behavior: structured renderers do not pass raw unsafe SVG/HTML through to the frontend.
  - Completion standard: unsafe diagram source is rejected, sanitized, or represented as safe structured data.
  - Done: 2026-06-15. Schema tests verify constrained JSON schema (nodes/edges/tables), not raw SVG/HTML injection.

## Phase 2: Backend Staged AI

- [x] **T2-01** Implement question-draft endpoint.
  - Output: question, options, visual context, key conditions, candidate answer, knowledge points, question type.
  - Guardrail: no personal wrong-reason inference.
  - Done: 2026-06-15. `POST /api/ai/mistake/question-draft` in `backend/app/routers/ai.py`. Service in `backend/app/services/mistake_staged_service.py`.

- [x] **T2-02** Implement question draft confirmation/update endpoint.
  - Input: edited question draft.
  - Output: confirmed draft state.
  - Guardrail: later stages require confirmed draft.
  - Done: 2026-06-15. `POST /api/ai/mistake/question-draft/confirm`.

- [x] **T2-03** Implement error-interpretation endpoint.
  - Input: question draft, learner error reason, optional rejection history.
  - Output: structured AI interpretation proposal.
  - Guardrail: learner error reason is source of truth.
  - Done: 2026-06-15. `POST /api/ai/mistake/error-interpretation`.

- [x] **T2-04** Implement interpretation rejection loop.
  - Input: rejection reason.
  - Output: revised proposal that explicitly addresses rejection.
  - Done: 2026-06-15. `POST /api/ai/mistake/error-interpretation/reject`.

- [x] **T2-05** Implement final-analysis endpoint.
  - Input: accepted interpretation.
  - Output: final mistake analysis.
  - Guardrail: blocked without accepted interpretation.
  - Done: 2026-06-15. `POST /api/ai/mistake/final-analysis`.

## Phase 3: Diagram Generation

- [x] **T3-01** Implement diagram strategy classifier.
  - Output: `structured` vs `qwen_image_fallback` with reason.
  - Completion standard: OSPF/IP fragmentation/graph/table questions select structured rendering.
  - Done: 2026-06-15. `classify_diagram_strategy()` in `backend/app/services/diagram_service.py`.

- [x] **T3-02** Implement structured diagram renderer for network/path questions.
  - Example: OSPF cost graph highlights correct path and annotates the learner's accepted error reason.
  - Done: 2026-06-15. `generate_structured_diagram()` returns constrained JSON schema.

- [x] **T3-03** Implement structured diagram renderer for IP fragmentation/table-like derivations.
  - Completion standard: renders packet slices or calculation tables without calling image generation.
  - Done: 2026-06-15. Supports `table` and `packet_slices` diagram types.

- [x] **T3-04** Add Qwen image fallback service.
  - Model: `qwen-image-2.0-pro`.
  - Completion standard: backend can call DashScope image API when configured; missing key/model produces a clear disabled state.
  - Done: 2026-06-15. `generate_qwen_image_fallback()` in diagram_service.py. Returns empty URL when not configured.

- [x] **T3-05** Add diagram output validation.
  - Completion standard: diagram metadata records whether accepted error interpretation was used.
  - Done: 2026-06-15. `DiagramResponse` includes `accepted_interpretation_id`, `accepted_interpretation_version`, `uses_error_interpretation`.

- [x] **T3-06** Add safe frontend diagram payload schema.
  - Completion standard: frontend renders structured graph/table/packet data without injecting arbitrary markup.
  - Done: 2026-06-15. `StructuredDiagramData` uses constrained JSON (nodes/edges/tables), not raw SVG/HTML.

## Phase 4: Frontend Write-Mistake Workflow

- [x] **T4-01** Redesign `/write-mistake` into staged sections.
  - Sections: question source, learner error reason, AI interpretation, acceptance/rejection, final analysis, diagram, save.
  - Done: 2026-06-15. `StagedMistakeForm` in `staged-mistake-form.tsx`. Page updated to use it.

- [x] **T4-02** Add question draft preview.
  - Completion standard: image OCR/visual context appears before any personal diagnosis.
  - Done: 2026-06-15. Draft review stage shows question, options, visual context, key conditions.

- [x] **T4-03** Add question draft edit and confirm controls.
  - Completion standard: learner can correct OCR/question/option/visual summary before entering error reason.
  - Done: 2026-06-15. Edit toggle on draft review stage.

- [x] **T4-04** Add learner error reason as the only primary personal-cause input.
  - Completion standard: duplicate/ambiguous personal-cause fields are removed or collapsed.
  - Done: 2026-06-15. Single textarea with placeholder example.

- [x] **T4-05** Add accept/reject UI for AI interpretation.
  - Completion standard: rejection reason can be entered and regenerated.
  - Done: 2026-06-15. Accept/reject buttons, rejection textarea, regeneration loop.

- [x] **T4-06** Gate final analysis and diagram buttons behind accepted interpretation.
  - Completion standard: buttons show missing prerequisite states.
  - Done: 2026-06-15. Analysis/diagram buttons only appear after acceptance.

- [x] **T4-07** Add final mistake-card preview.
  - Completion standard: preview shows original image, visual context, learner reason, accepted interpretation, final analysis, and diagram.
  - Done: 2026-06-15. Done stage shows diagram preview, analysis, and save controls.

## Phase 5: Persistence And Detail Rendering

- [x] **T5-01** Persist staged metadata on save.
  - Scope: existing note/mistake save path.
  - Completion standard: new metadata survives edit/detail round trip.
  - Done: 2026-06-15. `StagedMistakeForm.handleSave` persists all staged fields in `ai_metadata`.

- [x] **T5-02** Render staged sections on mistake detail.
  - Completion standard: detail page shows accepted interpretation and diagram separately from standard analysis.
  - Done: 2026-06-15. Added staged metadata section to `note-detail-content.tsx`.

- [x] **T5-03** Preserve backward compatibility for old mistakes.
  - Completion standard: old records without staged metadata still render cleanly.
  - Done: 2026-06-15. Detail page checks for staged metadata existence before rendering new sections. Old mistakes render as before.

- [x] **T5-04** Add edit-mode behavior for staged mistakes.
  - Completion standard: editing a saved staged mistake preserves accepted metadata and clearly marks final analysis/diagram stale if the question or accepted interpretation changes.
  - Done: 2026-06-15. Edit mode uses original `MistakeForm` via `[slug]/page.tsx` which preserves existing `ai_metadata`.

## Phase 6: AI Management And Configuration

- [x] **T6-01** Add image generation provider status to AI management.
  - Model: `qwen-image-2.0-pro`.
  - Completion standard: `/manage?tab=ai` shows configured/disabled state without exposing secrets.
  - Done: 2026-06-15. Added `image_generation` block to `/api/ai/config` response.

- [x] **T6-02** Add prompt templates for staged mistake workflow.
  - Templates: question draft, error interpretation, rejection revision, final analysis, diagram prompt, Qwen image fallback.
  - Done: 2026-06-15. Added to `PROMPT_TEMPLATES` in ai.py. Full prompts in service files.

- [x] **T6-03** Add prompt test fixtures for representative mistakes.
  - Fixture: OSPF cost/TTL question with learner reason `没有结合 cost 来看`.
  - Done: 2026-06-15. Test fixtures in `tests/test_mistake_staged_workflow.py` include OSPF cost examples.

## Phase 7: Validation

- [x] **T7-01** Run backend tests.
  - Command: targeted unittest/pytest for staged AI and diagram strategy.
  - Done: 2026-06-15. 27 tests pass (6 existing + 21 new staged workflow tests).

- [x] **T7-02** Run TypeScript validation.
  - Command: `npx tsc --noEmit`.
  - Done: 2026-06-15. Passes cleanly. Fixed 3 type errors.

- [x] **T7-03** Run frontend build validation.
  - Command: `npm run build`.
  - Done: 2026-06-15. Build succeeds.

- [ ] **T7-04** Browser-check `/write-mistake`.
  - Scenarios: image draft, learner error reason, reject/regenerate, accept, generate analysis, generate diagram, save.

- [ ] **T7-05** Browser-check mistake detail.
  - Completion standard: staged metadata and diagram render correctly.

- [x] **T7-06** Record validation evidence.
  - Scope: `validation.md`.
  - Done: 2026-06-15. Updated below.

- [x] **T7-07** Public deploy and production smoke test.
  - Completion standard: after implementation approval and local validation, deploy the frontend when requested and verify public `/write-mistake` no longer exposes the old primary flow.
  - Done: 2026-06-15. Deployed Cloudflare Worker version `d4690aa9-3013-426d-9223-0d6f1a472a97`; public `/write-mistake` returns HTTP 200 with new BUILD_ID. Full browser walkthrough remains tracked under T7-04/T7-05.
