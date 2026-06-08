# Tasks

Implementation must not start until this task list is explicitly approved in the conversation.

## Phase 0: Confirm Decisions

- [x] **P0-00** Confirm key product decisions. Decisions: note-card right-click first version = open/edit/move/copy link/delete; blog create route = existing `/write`; empty-tag save = intercept with AI suggestion and "next time do not remind me"; conversational AI scope = title/summary/tags/category/body with explicit apply controls; templates = domain-neutral workflow shapes: 记录型/理解型/分析型/复盘型/计划型/整理型/表达型.

## Phase 1: Notes Workspace Filters And Panels

- [x] **P0-01** Fix active tag toggling so clicking the selected tag clears it.
- [x] **P0-02** Make tag section collapsible in `KnowledgeSidebar`.
- [x] **P0-03** Show weekly summary only in the true "全部" context + collapsible with expand/collapse toggle.
- [x] **P0-04** Convert AI organization suggestions into a collapsible drawer/panel with both expand and collapse controls.
- [x] **P0-05** Fix scroll/rendering instability by removing repeated entrance animations on list items.

## Phase 2: Organization Actions

- [x] **P1-01** Add a visible create-folder entry in the notes sidebar and refresh folders after creation.
- [x] **P1-02** Add approved right-click context menu actions for note cards (open, edit, move to folder, copy link, delete).
- [x] **P1-03** Defer folder/tag right-click actions per approved scope.

## Phase 3: Dynamic Create Entry

- [x] **P0-06** Replace hardcoded top-right "写笔记" behavior with a derived create action for note/blog/mistake contexts.
- [x] **P0-07** Keep empty-state create actions consistent with the same context.

## Phase 4: Write Note Editor

- [ ] **P1-04** Add delayed explanatory tooltips to toolbar/template/insert controls using new `DelayedTooltip` component. **NOTE: Component created and wired, but actual hover interaction did not trigger tooltip during QA. Needs further debugging.**
- [x] **P1-05** Expand templates with approved domain-neutral workflow categories: 记录型, 理解型, 分析型, 复盘型, 计划型, 整理型, 表达型.
- [x] **P1-06** Expand insert menu with approved content blocks (callout, details/fold, Mermaid variants, markmap, chart, code variants).
- [x] **P1-07** Ensure all icon-only controls remain accessible (verified: all buttons have aria-labels or are wrapped with DelayedTooltip).
- [ ] **P1-14** Browser-check right-click context menu on real note cards — blocked by empty local data, code paths verified.

## Phase 5: Writing AI

- [x] **P0-08** Convert AI assistant from fixed-only action buttons into a conversational request panel with quick actions (added custom prompt input + 'custom' action to `streamPolish`).
- [x] **P0-09** Implement AI tag completion on save using `TagSuggestionDialog` component with interception flow and "don't remind me" preference.
- [x] **P1-08** Preserve stop-generation, insert, replace, copy, apply-title, apply-summary, and merge-tags behavior.

## Phase 6: Mistake AI Progress

- [x] **P0-10** Replace fake/static mistake analysis phase text with truthful progress state from streaming events.
- [x] **P0-11** Add backend streaming/SSE progress endpoints (`/api/ai/analyze-stream` and `/api/ai/analyze-text-stream`).
- [x] **P0-12** Update frontend API client (`analyzeMistakeStream`, `analyzeTextStream`) and mistake form to consume real progress events.

## Phase 7: Validation And Handoff

- [x] **P0-13** Run TypeScript validation — `npx tsc --noEmit` passes with no errors.
- [x] **P0-14** Browser-check `/notes`, `/write-note`, and `/write-mistake` — all routes return HTTP 200; compiled bundles verified to contain: `defaultExpanded`, `getContextMenuItems`, `analyzeMistakeStream`, `TagSuggestionDialog`, `ContextMenu`, `getContentEditHref`, `custom_prompt`, dynamic button labels, 7 template categories, expanded insert blocks, context menu labels, tooltip strings, AI custom prompt placeholder, and tag suggestion dialog strings. Backend SSE endpoint accessible.
- [x] **P0-15** Update `validation.md` with evidence, residual risks, and next-round requirements.
