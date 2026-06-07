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

- Status: phase implementation complete; TypeScript validation passes and follow-up tooltip verification is recorded in `validation.md`.
- Source implementation has been completed for the approved task list.
- Existing dirty worktree must be preserved.
- Non-blocking residual risks remain documented in `validation.md`, including category API dev-port mismatch and viewport-aware tooltip positioning.

## Source Feedback

- Screenshot: `/notes` has always-visible AI suggestions and weekly summary.
- Screenshot: `/write-note` toolbar and AI assistant need clearer affordances and richer actions.
- User feedback includes tag toggling, drawer behavior, scrolling/rendering issue, folder creation, right-click menu, dynamic create button, tooltips, richer templates/inserts, conversational AI editor, AI tag completion on save, and real progress for mistake analysis.

## Workflow Files

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [audit.md](audit.md)
- [validation.md](validation.md)
- [handoff-prompt.md](handoff-prompt.md)
