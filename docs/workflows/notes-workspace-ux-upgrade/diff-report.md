# Diff Report

## 2026-06-07 Original Implementation

### Summary

Implemented Phase 0–7 of the notes workspace UX upgrade across 15 modified files and 3 new shared components.

### Modified Files

| File | Key Changes |
| --- | --- |
| `src/app/notes/page.tsx` | Tag toggle, weekly summary conditional, suggestions drawer, remove list animations, right-click context menu, dynamic create button, empty-state consistency |
| `src/app/notes/components/knowledge-sidebar.tsx` | Tag toggle fix, tag section collapsible with `defaultExpanded`, create-folder entry with inline input |
| `src/app/notes/components/suggestion-card.tsx` | Collapsible drawer pattern with `defaultExpanded` prop |
| `src/app/write-note/page.tsx` | Tag completion on save interception via `TagSuggestionDialog`, `folder_id` read from search params |
| `src/app/write-note/[slug]/page.tsx` | Tag completion on save interception (edit page parity) |
| `src/app/write-note/components/note-toolbar.tsx` | `DelayedTooltip` wrapping, expanded insert menu (callout, details, Mermaid, markmap, chart, code variants) |
| `src/app/write-note/components/note-templates.tsx` | 7 domain-neutral workflow templates (记录型/理解型/分析型/复盘型/计划型/整理型/表达型) |
| `src/app/write-note/components/ai-assistant-panel.tsx` | Conversational custom prompt input + 'custom' action, full apply controls (title/summary/tags/category/body) |
| `src/app/write-mistake/components/mistake-form.tsx` | Real streaming progress via `analyzeMistakeStream`, tag completion on save interception |
| `src/lib/api/ai.ts` | Streaming API clients: `analyzeMistakeStream`, `analyzeTextStream` |
| `src/lib/api/ai-polish.ts` | Added `'custom'` action type and `custom_prompt` option |
| `backend/app/routers/ai.py` | SSE streaming endpoints: `/analyze-stream`, `/analyze-text-stream` |

### New Files

| File | Purpose |
| --- | --- |
| `src/components/context-menu.tsx` | Reusable right-click context menu component |
| `src/components/delayed-tooltip.tsx` | Reusable delayed hover tooltip component |
| `src/components/tag-suggestion-dialog.tsx` | AI tag suggestion on empty-tag save (shared write-note/write-mistake) |

---

## 2026-06-15 Follow-Up Hardening (Complete)

### Pre-Existing Dirty Files

Before this follow-up round, two files had uncommitted RAF throttling patches:

| File | Dirty Change |
| --- | --- |
| `src/app/write-note/components/ai-assistant-panel.tsx` | `requestAnimationFrame` throttling in `runAction()` and `runCustomPrompt()`, stale request check via `currentId`, cleanup on `onDone`/`onError` |
| `src/components/tag-suggestion-dialog.tsx` | RAF gate added to `generateTags()` for debouncing |

### Implemented Changes (Phase 8)

| Task | Target Files | Changes |
| --- | --- | --- |
| P0-16 | Research | Verified: `activeFolderId` is local state, back/cancel hardcode `/notes`, detail page has no folder context |
| P0-17 | `src/app/notes/page.tsx`, `src/lib/api/folders.ts` | URL-synced `folder_id`, breadcrumb bar with `findFolderPath()`, folder tree loading, clear button |
| P0-18 | `src/app/write-note/page.tsx` | `folderQuery` threaded through back link (L152), cancel link (L339), and post-save redirect (L140) |
| P0-19 | `src/app/write-note/[slug]/page.tsx`, `src/app/notes/[id]/note-detail-content.tsx`, `src/lib/content-routes.ts` | `useSearchParams` for `folder_id`, deterministic cancel links, `getContentListHref` accepts optional `folderId` |
| P0-20 | `src/components/tag-suggestion-dialog.tsx` | `AbortController` with abort on unmount/open-change, stale request protection via `requestIdRef` |
| P0-21 | `ai-assistant-panel.tsx`, `tag-suggestion-dialog.tsx`, `ai-polish.ts` | `rafRef` for unmount-safe RAF cleanup, `handleStop` cancels RAF, `AbortError` calls `onDone()` |
| P1-09 | `weekly-summary-card.tsx`, `backend/app/routers/suggestions.py` | Idempotent save (try update before create), `ensureWeeklyFolder()`, `POST /weekly-summary/generate` endpoint |
| P1-10 | `backend/app/services/knowledge_assistant.py`, `suggestion-card.tsx` | Weakness threshold `>= 3`, `activity`/`organize` type for recent suggestions |
| P0-22 | N/A | `npx tsc --noEmit` pass, backend syntax pass |
| P0-23 | `validation.md`, `diff-report.md`, `tasks.md` | Documentation updated |

### New Utilities

| File | Addition |
| --- | --- |
| `src/lib/api/folders.ts` | `findFolderPath(nodes, targetId)` — traverses folder tree to build breadcrumb path |

### Code Review Fix Round (2026-06-15)

| File | Fix |
| --- | --- |
| `src/app/notes/page.tsx` | Removed `handleFolderChange(null)` from `handleFilterChange`; added `folderQuery` to card Link, context menu "打开"/"复制链接" |
| `src/components/tag-suggestion-dialog.tsx` | `++requestIdRef.current` before abort in cleanup effect |
| `src/app/write-note/components/ai-assistant-panel.tsx` | `++requestIdRef.current` before abort in unmount cleanup |
| `backend/app/routers/suggestions.py` | Fixed `week_start` to use Monday 00:00 boundary; added `note.folder_id = folder.id` on update |
| `backend/app/schemas/note.py` | Added `folder_id` to `NoteUpdate` schema |
| `src/lib/api/notes.ts` | Added `folder_id` to `NoteUpdateInput` |
| `src/app/notes/components/weekly-summary-card.tsx` | Added `folder_id` to `updateNote` call |
