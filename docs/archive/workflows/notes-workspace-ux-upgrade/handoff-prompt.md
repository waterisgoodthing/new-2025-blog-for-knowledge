# Handoff Prompt

Continue the `notes-workspace-ux-upgrade` workflow — **Phase 8: 2026-06-15 Follow-Up Hardening**.

Before implementation:

1. Read `README.md`, `requirements.md`, `design.md`, and `tasks.md` (Phase 8 section).
2. Confirm that Phase 8 `tasks.md` was explicitly approved in the conversation.
3. Preserve existing dirty files: `src/app/write-note/components/ai-assistant-panel.tsx` and `src/components/tag-suggestion-dialog.tsx` already have RAF throttling patches — harden them in place.
4. Follow the repository `AGENTS.md` workflow and update `tasks.md` immediately after each completed task.
5. Run `npx tsc --noEmit` after frontend changes. Run backend import checks if backend files change.

## Phase 8 Follow-Up Feedback

New user-reported issues from 2026-06-15:

1. Folder placement is not OS-like enough — needs breadcrumb, active-location clarity, and clear "where am I" indicators.
2. Creating a note from inside a folder still requires manual classification — `folder_id` should carry through create, save, and return navigation.
3. AI-generated tags disappeared — tag generation in both `TagSuggestionDialog` and AI assistant tag action needs to be restored and hardened.
4. Returning from note edit/detail to overview loses the active folder — folder context must be preserved in URL params and threaded through back/cancel links.
5. Weekly summary should run Monday 08:00, display in workspace, and save into a dedicated folder — needs scheduling and idempotent persistence.
6. AI suggestions are too broad — weak-point claims must require mistake/review evidence, not just frequent uploads.
7. Streaming render RAF fix needs hardening — cancel pending frames on unmount/done/error/abort, add AbortController to tag dialog.

## Key Technical Context

- `folder_id` URL param approach: `src/app/notes/page.tsx` already passes `activeFolderId` to create action, but does not read/write it from URL.
- `src/app/write-note/page.tsx` already reads `folder_id` from search params and sends it on create — but back/cancel links hardcode `/notes`.
- `src/lib/content-routes.ts` has no `folderId` parameter support.
- `backend/app/services/knowledge_assistant.py` weakness threshold is `>= 2` — should be `>= 3`.
- `ai-polish.ts` silently swallows `AbortError` without calling `onDone`/`onError` — callers cannot clean up RAF.

