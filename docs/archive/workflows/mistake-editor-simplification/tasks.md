# Tasks: Mistake Editor Simplification

Version: v0.1
Date: 2026-06-23
Status: Drafted, awaiting user approval
Sources: `requirements.md`, `design.md`

## Approval Gate

- [ ] **APPROVAL**: User explicitly approved this task list in conversation.

Implementation must not start before this checkbox can be marked complete.

## Phase 0: Baseline And Root Cause

- [ ] **T0-1**: Record baseline and unrelated dirty files.
  - Priority: P0
  - Domains: `mistakes`
  - Files: `validation.md`
  - Work: Record `git status --short`, current branch, and note unrelated dirty files before source edits.
  - Completion standard: Baseline evidence is written to `validation.md`.

- [ ] **T0-2**: Identify the Mermaid error source.
  - Priority: P0
  - Domains: `mistakes`, shared infrastructure
  - Files: `validation.md`, possibly `audit.md`
  - Work: Inspect `MermaidBlock`, shared markdown rendering, note detail diagram rendering, and `/mistakes` DOM/browser evidence.
  - Completion standard: `validation.md` states the likely source and reproduction status.

## Phase 1: Unified Mistake Editor

- [ ] **T1-1**: Rehydrate staged editor state from an existing mistake.
  - Priority: P0
  - Requirements: REQ-01, REQ-02, REQ-03
  - Files: `src/app/write-mistake/components/staged-mistake-form.tsx`
  - Work: Add edit-mode props and initialize state from `NoteDetail` first-class fields plus staged AI metadata.
  - Completion standard: Existing mistake data appears in the same editor surface used by new mistakes.

- [ ] **T1-2**: Add edit-mode save path to the staged editor.
  - Priority: P0
  - Requirements: REQ-01, REQ-02
  - Files: `src/app/write-mistake/components/staged-mistake-form.tsx`
  - Work: Use `updateNote(initialData.slug, payload)` in edit mode and preserve create behavior with `createNote`.
  - Completion standard: Editing an existing mistake updates that note and does not create a duplicate.

- [ ] **T1-3**: Route `/write-mistake/[slug]` to the unified editor.
  - Priority: P0
  - Requirements: REQ-01
  - Files: `src/app/write-mistake/[slug]/page.tsx`
  - Work: Replace legacy `MistakeForm` usage with the unified staged editor in edit mode.
  - Completion standard: Create and edit routes share the same component family and visual model.

- [ ] **T1-4**: Retire or isolate the old editor.
  - Priority: P1
  - Requirements: REQ-01
  - Files: `src/app/write-mistake/components/mistake-form.tsx`, references
  - Work: Remove unused legacy component or leave a clearly unused fallback only if another route still depends on it.
  - Completion standard: No active mistake route uses two competing editor implementations.

## Phase 2: Editor Visual Simplification

- [ ] **T2-1**: Simplify the staged editor layout.
  - Priority: P0
  - Requirements: REQ-04, REQ-07
  - Files: `src/app/write-mistake/components/staged-mistake-form.tsx`
  - Work: Reduce nested cards, tighten spacing, create a calmer toolbar/status area, and keep controls accessible.
  - Completion standard: New and edit pages look like one polished operational editor.

- [ ] **T2-2**: Make AI sections progressive.
  - Priority: P1
  - Requirements: REQ-03, REQ-04
  - Files: `src/app/write-mistake/components/staged-mistake-form.tsx`
  - Work: Keep completed AI interpretation, analysis, and diagram visible but collapsible/regenerable rather than forcing a long vertical flow.
  - Completion standard: Edit mode can review existing AI outputs without replaying all steps.

## Phase 3: `/mistakes` Page Simplification

- [ ] **T3-1**: Remove duplicate review/action noise.
  - Priority: P0
  - Requirements: REQ-05
  - Files: `src/app/mistakes/page.tsx`
  - Work: Consolidate review CTA and compact the stats/review plan presentation.
  - Completion standard: The first viewport has one obvious review action and no repeated review blocks.

- [ ] **T3-2**: Collapse or drawer-ize weak-point diagnosis by default.
  - Priority: P0
  - Requirements: REQ-05
  - Files: `src/app/mistakes/page.tsx`, `src/app/mistakes/components/weak-point-diagnosis.tsx`
  - Work: Keep weak-point insight accessible but no longer as a large always-open section.
  - Completion standard: The mistake list becomes the dominant content after the toolbar/filter area.

- [ ] **T3-3**: Tighten mistake list item density.
  - Priority: P1
  - Requirements: REQ-05, REQ-07
  - Files: `src/app/mistakes/page.tsx`
  - Work: Preserve title, date, review state, difficulty, subject, and useful tags while reducing visual clutter.
  - Completion standard: List remains scannable and does not feel like repeated large cards.

## Phase 4: Mermaid Error Containment

- [ ] **T4-1**: Harden Mermaid rendering against leaked parser artifacts.
  - Priority: P0
  - Requirements: REQ-06
  - Files: `src/components/mermaid-block.tsx`, possibly shared markdown rendering
  - Work: Ensure invalid Mermaid syntax renders only a compact local fallback and clears any previous output.
  - Completion standard: Invalid Mermaid cannot produce a large `Syntax error in text mermaid version...` overlay.

- [ ] **T4-2**: Prevent invalid diagram metadata from surfacing on list/detail UI.
  - Priority: P1
  - Requirements: REQ-06
  - Files: `src/app/notes/[id]/note-detail-content.tsx` or AI metadata rendering path if needed
  - Work: Skip or label invalid diagram content where cheap validation can catch it.
  - Completion standard: Saved invalid diagram metadata does not break page presentation.

## Phase 5: Validation And Documentation

- [ ] **T5-1**: Run TypeScript validation.
  - Priority: P0
  - Requirements: AC-06
  - Files: `validation.md`
  - Work: Run `npx tsc --noEmit` and record result.
  - Completion standard: Pass recorded, or first relevant failure documented.

- [ ] **T5-2**: Browser inspect key routes.
  - Priority: P0
  - Requirements: AC-01 through AC-07
  - Files: `validation.md`, optionally `assets/`
  - Work: Inspect `/mistakes`, `/write-mistake`, and `/write-mistake/[slug]`; include desktop and at least one narrow viewport if layout changed substantially.
  - Completion standard: Evidence confirms unified editor, simplified list, and no Mermaid error overlay.

- [ ] **T5-3**: Update workflow docs and diff report.
  - Priority: P1
  - Requirements: all
  - Files: `tasks.md`, `validation.md`, `diff-report.md`
  - Work: Mark each task complete immediately after finishing it, record validation, and summarize final changed files.
  - Completion standard: No completed implementation task lacks validation notes.
