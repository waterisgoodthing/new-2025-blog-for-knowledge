# Batch 1 Route Current State

## Scope

Touched line: frontend / manage shell.

This audit records the current route state for Batch 1 UI Shell & Learning Workspace Entry. It does not approve database, backend, API, Subject, Question, Mistake, Review, Attachment, OCR, or AI implementation.

## Architecture Context Read

Read:

- `docs/architecture/personal-learning-system-v2.md`
- `docs/architecture/domains.md` as the current `functional-boundaries.md` equivalent
- `docs/architecture/routes.md` as the current `target-routes.md` equivalent
- `docs/architecture/ui-redesign.md`
- `docs/architecture/mvp-scope.md`
- `docs/architecture/implementation-phases.md`
- `docs/workflows/mvp-rebuild-batch-1-ui-shell/*`

The requested filenames `functional-boundaries.md` and `target-routes.md` do not exist in `docs/architecture/`; the current canonical equivalents are `domains.md` and `routes.md`.

## Current Public Routes

Confirmed route files under `src/app` include:

- `/`
- `/blog`
- `/blog/[id]`
- `/notes`
- `/notes/[id]`
- `/mistakes`
- `/about`
- `/discover`
- `/guestbook`
- `/music`
- `/pictures`
- `/projects`
- `/share`
- `/snippets`
- `/svgs`
- `/clock`
- `/image-toolbox`
- `/live2d`
- `/wuthering-waves`

Compatibility editor routes also exist:

- `/write`
- `/write/[slug]`
- `/write-note`
- `/write-note/[slug]`
- `/write-mistake`
- `/write-mistake/[slug]`
- `/mistakes/review`

Batch 1 did not change these public or compatibility routes.

## Current Manage Routes

Existing root:

- `/manage` remains the legacy login and management entry.

Batch 1 shell routes under `src/app/manage/(workspace)`:

- `/manage/dashboard`
- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`
- `/manage/questions`
- `/manage/questions/[id]`
- `/manage/mistakes`
- `/manage/mistakes/[id]`
- `/manage/review`
- `/manage/attachments`
- `/manage/attachments/[id]`
- `/manage/ai`
- `/manage/ai/runs`
- `/manage/jobs`
- `/manage/search`
- `/manage/analytics`
- `/manage/settings`
- `/manage/capture`
- `/manage/drafts`
- `/manage/drafts/[id]`

The route group keeps the URL shape as `/manage/**` while allowing `/manage` itself to remain outside the new `AuthGate` layout and avoid redirect loops.

## Existing Components

Management shell components:

- `ManageSidebar`
- `ManageTopbar`
- `ManagePageHeader`
- `ManageMobileNav`
- `ManagePlaceholderPage`
- `ManageEmptyState`
- `ManagePanel`
- `ManageStatusBadge`
- `ManageTableContainer`
- `ManageFormPanel`

Public entry component:

- `LearningSpaceCard`

Existing later-batch components are still present under route component folders, but current Batch 1 page entries have been frozen to static placeholders rather than importing those business components.

## Conflicts And Compatibility Needs

- `/manage/page.tsx` has legacy login and management behavior. It must remain reachable and was not moved into the protected workspace layout.
- Existing later-batch files and API clients are present in the worktree. Batch 1 page entries must not import them or trigger real learning workflows.
- `/manage/**` protected shell uses `AuthGate` for page access experience only.
- Frontend protection is not a security boundary. Backend admin APIs remain the real future security boundary.
- Public pages must stay low-density and publicly readable; the homepage must not become a dashboard.

## Current Batch 1 Freeze Result

- Route shell exists.
- Sidebar has the required placeholder entries.
- Dashboard and future containers use static content.
- Accessible Batch 1 page entries do not call learning, AI, upload, review, or database APIs.
- No backend, database, migration, or API client file was modified in this Batch 1 pass.
