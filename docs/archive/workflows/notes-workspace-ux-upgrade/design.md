# Design

## Visual Thesis

A quiet, dense personal knowledge cockpit: collapsible navigation, contextual panels, and a writing surface that reveals help only when needed.

## Content Plan

- Notes workspace: navigation drawer/sidebar, search/filter row, contextual create action, collapsible AI organization drawer, optional weekly summary, stable note list.
- Writing workspace: title/slug/type metadata, editor toolbar with delayed tooltips, rich template/insert menus, conversational AI assistant drawer.
- Mistake workspace: image/text analysis with real progress states and clear apply/save flow.

## Interaction Thesis

- Use drawers and collapsible sections to reduce visual noise without hiding important controls.
- Use delayed tooltips for toolbar learning, not visible instructional text.
- Use event-driven progress for AI workflows so the UI feels honest rather than decorative.

## Current Code Map

- `/notes`: `src/app/notes/page.tsx`
- Knowledge sidebar: `src/app/notes/components/knowledge-sidebar.tsx`
- AI suggestions: `src/app/notes/components/suggestion-card.tsx`
- Weekly summary: `src/app/notes/components/weekly-summary-card.tsx`
- Note editor: `src/app/write-note/page.tsx`
- Edit note editor: `src/app/write-note/[slug]/page.tsx`
- Toolbar: `src/app/write-note/components/note-toolbar.tsx`
- Templates: `src/app/write-note/components/note-templates.tsx`
- Slash insert menu: `src/app/write-note/components/slash-command-menu.tsx`
- AI writing assistant: `src/app/write-note/components/ai-assistant-panel.tsx`
- Mistake form: `src/app/write-mistake/components/mistake-form.tsx`
- AI routes: `backend/app/routers/ai.py`
- AI API client: `src/lib/api/ai.ts`

## Architecture

### Frontend

Use existing route-local components for route-specific behavior. Shared primitives can live in `src/components/` only if reused by notes and write-note:

- `ContextMenu` if right-click is used across notes/folders/tags.
- `DelayedTooltip` if toolbar, sidebar, and action buttons share it.
- `DrawerPanel` only if drawer behavior is reused beyond one component.

Keep API calls flowing through `src/lib/api/*`.

### Backend

Only touch backend AI route if real progress streaming is approved for this pass. The preferred design is:

```text
frontend EventSource/fetch stream -> /api/ai/analyze-stream -> async generator events -> model call boundaries -> final JSON
```

If the AI provider does not expose granular progress, the backend should still emit truthful coarse events:

1. `received`
2. `validating_input`
3. `calling_model`
4. `parsing_model_output`
5. `finding_related_notes`
6. `done`

No fake step timers.

## Page Design

### Notes Workspace

- Sidebar:
  - content filters remain top.
  - folder section gets a visible create button.
  - tag section becomes collapsible.
  - clicking active tag toggles it off.
- Main header:
  - create action is computed from active context.
  - search remains compact.
- Context panels:
  - weekly summary shown only for the all-context dashboard.
  - AI suggestions shown as a collapsed drawer trigger by default.
- List:
  - reduce repeated entrance animation on every item during pagination/scroll.
  - inspect scroll blank/render issue with browser tooling before patching.

### Right-Click Menu

First pass decision:

- Note card menu:
  - Open
  - Edit
  - Move to folder
  - Copy link
  - Delete
- Deferred optional actions:
  - Duplicate
  - Add tag
  - Hide/archive
  - Folder create child/rename/delete/move actions
  - Tag rename/merge/remove actions

### Write Note Workspace

- Add delayed tooltips around toolbar controls.
- Expand template menu with abstract workflow shapes rather than subject-specific presets:
  - Capture
  - Understand
  - Analyze
  - Review
  - Plan
  - Organize
  - Express
- Expand insert menu:
  - callout blocks
  - details/fold block
  - Mermaid graph/state/timeline
  - markmap
  - chart JSON
  - review card
  - code block variants
- AI assistant:
  - keep quick actions as shortcuts.
  - add text input for custom instruction.
  - operate on selection when present, otherwise full content.
  - support aggressive apply targets: title, summary, tags, category, and body content.
  - expose explicit apply/confirm controls for each target so AI does not silently overwrite fields.

## State Changes

- `activeTag`: string/null; clicking same tag should set null.
- `activeFilter`: use one context source where possible; avoid divergence between top type pills and sidebar filters.
- `createAction`: derived from active filter/type/tag/folder context.
- `suggestionsOpen`: local UI state.
- `tagsCollapsed`: local UI state.
- `aiCustomPrompt`: AI assistant state.
- `skipEmptyTagReminder`: persisted client preference for "next time do not remind me".
- `pendingAiTagSuggestion`: generated tags shown during save interception.
- `analysisProgress`: event list/current event from stream.

## API Design

### Existing APIs Reused

- `listNotes`
- `createNote`
- `updateNote`
- folder APIs in `src/lib/api/folders`
- AI polish APIs for writing assistant where adequate

### Potential New API

If implementing truthful mistake progress:

```text
POST /api/ai/analyze-stream
Body: AnalyzeRequest
Auth: admin/JWT consistent with existing analyze endpoint
Response: text/event-stream or newline-delimited JSON events
Events:
  progress: { step, label }
  result: AnalyzeResponse
  error: { message }
```

## Exception Design

- Suggestions fail: drawer shows "暂时无法加载建议" and retry.
- Weekly summary fails: hidden or compact error, page still works.
- Folder create fails: toast with API message.
- AI tag suggestion fails: explain failure and allow save without generated tags.
- Empty-tag reminder disabled: save proceeds without interception.
- Stream disconnects: show last completed step and retry.

## Validation Plan

- `npx tsc --noEmit` for frontend TypeScript changes.
- Browser check `/notes`, `/write-note`, `/write-mistake`.
- Manual checks:
  - tag select/unselect.
  - weekly summary visibility by filter.
  - AI suggestion drawer open/close.
  - create folder and list refresh.
  - dynamic create action per context.
  - editor tooltips after hover delay.
  - template and insert menus.
  - AI assistant custom request.
  - mistake analysis progress states.
- If backend stream changes, run FastAPI import/start or targeted tests if present.

## 2026-06-15 Follow-Up Design

### Initial Findings

- `src/app/notes/page.tsx` already passes `folder_id` into `/write-note` when `activeFolderId` is set.
- `src/app/write-note/page.tsx` already reads `folder_id` from search params and sends it in `createNote`.
- The remaining folder-create complaint is likely in context preservation, route/back links, or a production/backend mismatch, not simply a missing create payload.
- `src/app/write-note/page.tsx` returns to plain `/notes` from the back and cancel links, so it can lose folder context.
- `src/app/notes/components/weekly-summary-card.tsx` saves a weekly summary note manually, but does not create/use a dedicated folder and does not schedule Monday 08:00 generation.
- `backend/app/services/knowledge_assistant.py` currently emits weak-point suggestions from aggregate mistake subjects/knowledge points, and recent-upload summaries from recent notes. The wording needs to distinguish organization/review evidence from upload frequency.
- Current dirty changes throttle streaming in `AIAssistantPanel` and `TagSuggestionDialog`, but need unmount cleanup and a clearer stale-request/cancel boundary.

### Proposed Direction

- Preserve folder context through URL query parameters first because `/notes` already supports `folder_id` as the API filter input and this avoids a new global state store.
- Add folder-aware back/cancel/create/detail/edit links where the notes flow owns the navigation.
- Re-check backend folder assignment contract before changing it; the earlier `folder-note-assignment-fix` workflow says this was already implemented and deployed.
- Restore AI tags by inspecting both `TagSuggestionDialog` and `AIAssistantPanel` tag flows, then fixing the smallest broken parsing/apply path.
- Implement weekly-summary persistence idempotently by week slug and a dedicated folder. Scheduling must be explicit: either backend scheduler/cron support if present, or a documented deployment cron endpoint if not.
- Update AI suggestions so weak-point claims require mistake/review evidence, while recent uploads only create neutral "recent activity" or organization suggestions.
- Harden streaming render throttling with a reusable helper or local refs/effects that cancel pending `requestAnimationFrame` callbacks on unmount, stop, done, error, and stale request transitions.

### Follow-Up Validation Plan

- Run `npx tsc --noEmit` for frontend TypeScript changes.
- Run targeted backend import/compile checks if backend AI/folder/weekly code changes.
- Browser-check `/notes` and `/write-note` folder-context round trips.
- Verify AI tag suggestion UI in both empty-tag save and AI assistant tag action.
- Verify weekly-summary persistence is idempotent for the same week.
- Record all results in `validation.md`.
