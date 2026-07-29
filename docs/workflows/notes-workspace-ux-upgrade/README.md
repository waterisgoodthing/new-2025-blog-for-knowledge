# Notes Workspace UX Upgrade

## Goal

Upgrade the notes workspace and writing flows based on the June 7, 2026 feedback screenshots and notes: collapsible side panels, correct filter behavior, dynamic create actions, folder creation entry, richer editor affordances, AI-assisted tagging, conversational writing AI, and truthful mistake-analysis progress.

## Touched Domains

- `notes`
- `mistakes`
- `review`
- `write-note`
- `write-mistake`
- `manage`
- shared frontend infrastructure
- backend `ai` only for progress streaming / real status feedback

## Current Status

- Status: Phase 0–7 original implementation complete and deployed. Phase 8 follow-up hardening (2026-06-15) implementation complete — all 10 tasks done.
- Source implementation has been completed for both original and follow-up task lists.
- Follow-up round modified 13 files across frontend and backend.
- `npx tsc --noEmit` and backend syntax checks pass.
- Remaining residual risk: weekly summary cron scheduling needs deployment configuration (endpoint exists).
- `diff-report.md` documents all changes from both rounds.

## 2026-06-15 Follow-Up Feedback

New user-reported issues:

1. The first folder placement is not OS-like enough.
2. Creating a note while located in a folder still requires manual classification afterward.
3. AI-generated tags disappeared.
4. Returning from the note edit page to overview does not restore the previous main folder.
5. Weekly summary should run every Monday at 08:00, display in the workspace, and be saved into a dedicated folder.
6. AI suggestions are too broad and should not infer weak knowledge from frequent recent uploads alone.
7. Streaming render performance was already patched in `ai-assistant-panel.tsx` and `tag-suggestion-dialog.tsx`; this round should harden that fix with cleanup and regression protection.

## Source Feedback

- Screenshot: `/notes` has always-visible AI suggestions and weekly summary.
- Screenshot: `/write-note` toolbar and AI assistant need clearer affordances and richer actions.
- User feedback includes tag toggling, drawer behavior, scrolling/rendering issue, folder creation, right-click menu, dynamic create button, tooltips, richer templates/inserts, conversational AI editor, AI tag completion on save, and real progress for mistake analysis.

## Workflow Files

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [audit.md](audit.md)
- [diff-report.md](diff-report.md)
- [validation.md](validation.md)
- [handoff-prompt.md](handoff-prompt.md)
