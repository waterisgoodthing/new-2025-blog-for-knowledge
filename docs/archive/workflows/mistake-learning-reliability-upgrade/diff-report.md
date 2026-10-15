# Diff Report: Expected Implementation Scope

Date: 2026-06-12
Status: Draft prediction only; no implementation has been performed.

## Purpose

This file predicts the source files likely to change when `tasks.md` is approved. It is a scope guard for implementation agents.

## Expected File Scope By Phase

### Phase 1: P0 Runtime Reliability

Likely files:

- `src/lib/api/client.ts`
- `src/lib/api/config.ts`
- `backend/app/routers/review.py`
- `backend/app/routers/notes.py`
- Optional backend helper under `backend/app/utils/` or `backend/app/services/`
- Optional frontend toast/call-site files if API errors need better display

Expected changes:

- Improve API error parsing and messages.
- Verify API base URL behavior.
- Normalize `Note` datetime writes in review, update, and type-conversion paths covered by this workflow.
- Add safe create-time slug suffixing or recovery.

Out of scope:

- Rewriting auth from scratch.
- Editing Cloudflare tunnel config without explicit user approval.

### Phase 2: Data And AI Contract

Likely files:

- `backend/app/schemas/ai.py`
- `backend/app/routers/ai.py`
- `src/lib/api/ai.ts`
- `src/app/write-mistake/components/mistake-form.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`

Expected changes:

- Add optional personal-answer fields to AI request contracts.
- Send personal fields from the form.
- Persist personalized diagnosis in `ai_metadata`.
- Display personalized diagnosis separately.
- Strengthen LaTeX output handling.

Out of scope:

- Adding a new database column unless the user approves a schema/migration expansion.
- Replacing the markdown renderer.

### Phase 3: Tag And Weak-Point Model

Likely files:

- `backend/app/services/knowledge_retrieval.py`
- `backend/app/schemas/knowledge.py`
- `backend/app/services/ai_polish_service.py`
- `backend/app/routers/ai.py`
- `src/lib/api/knowledge.ts`
- `src/app/mistakes/page.tsx`
- `src/app/notes/components/knowledge-sidebar.tsx`
- `src/app/write-mistake/components/mistake-form.tsx`
- Optional taxonomy helper under `backend/app/services/` or `src/lib/`

Expected changes:

- Add canonical concept metadata.
- Tighten AI tag prompts and save-time tag hygiene.
- Keep raw tags accessible but lower priority.
- Group related concepts such as exchange/switching terms.

Out of scope:

- Creating a full `KnowledgePoint` table.
- Bulk migrating all historical tags without an approved data migration plan.

### Phase 4: UI Layout And Drawer

Likely files:

- `src/app/mistakes/components/weak-point-diagnosis.tsx`
- `src/app/mistakes/page.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`
- Optional shared drawer component if an existing one is not available

Expected changes:

- Convert the full weak-point panel to a compact summary plus drawer.
- Replace static diagnosis copy with evidence-aware content.
- Move knowledge summary under tags in the detail right rail.

Out of scope:

- Marketing-style landing pages.
- Broad visual redesign unrelated to mistake learning.

### Phase 5: Validation And Documentation

Likely files:

- `docs/workflows/mistake-learning-reliability-upgrade/tasks.md`
- `docs/workflows/mistake-learning-reliability-upgrade/validation.md`
- Optional screenshots under `docs/workflows/mistake-learning-reliability-upgrade/assets/`

Expected changes:

- Mark completed tasks immediately.
- Record command output, browser checks, API checks, and residual risks.
