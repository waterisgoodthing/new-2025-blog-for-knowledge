# Current-State Audit

## Architecture Baseline

- `mvp-scope.md` defines Batch 7 as compatibility, small state closure, basic validation, dangerous-action confirmation, dead-link handling, and local trial notes.
- Batch 5 is closed and accepted.
- Batch 6 is closed and accepted.
- The independent public mistake review API gate is closed and accepted; its hook regression test confirms anonymous review APIs use `null` SWR keys.

## Route Facts

- Public routes include `/`, `/blog`, `/blog/[id]`, `/notes`, `/notes/[id]`, and `/mistakes`.
- Private manage routes are grouped under `src/app/manage/(workspace)/layout.tsx`, which wraps the workspace in `AuthGate`.
- `/mistakes/review`, `/write-note`, and `/write-mistake` have explicit page-level `AuthGate` wrappers.
- Legacy detail/edit route compatibility requires separate review before changing or redirecting `/write-note/[slug]` and `/write-mistake/[slug]`.
- The build output contains placeholder and active manage routes together; route existence alone does not prove correct data or permission behavior.

## Known Review Targets

1. Confirm edit-detail routes `/write-note/[slug]` and `/write-mistake/[slug]` use page-level protection.
2. Confirm public `/mistakes` and `/notes/[id]` never require admin APIs to render.
3. Audit links from home, sidebar, notes, mistake, and manage surfaces for stale or future-only destinations.
4. Check dangerous actions have confirmation and error recovery.
5. Document local trial commands and known pre-existing warnings.

## Database Facts (Read Only)

- Alembic revision: `020 (head)`.
- `notes=13`.
- `subjects=1`, `knowledge_points=3`.
- `question_drafts=3`, `questions=3`.
- `mistake_drafts=3`, `mistakes=3`, `review_items=3`, `review_records=4`.
- `attachments=1`, `attachment_links=1`.
- No Batch 7 migration or data mutation has been executed.

## Worktree Caution

The repository is already dirty with changes from earlier batches and adjacent workflows. Batch 7 must touch only approved compatibility files and its own workflow documents; unrelated changes must be preserved.

## P0-02 Compatibility Freeze

### Public Read Contract

The following routes remain anonymous-readable and must not require `AuthGate`:

| Route | Current contract | Admin-only behavior |
|---|---|---|
| `/` | Public home | Admin-only learning links are ordinary links to protected routes |
| `/blog`, `/blog/[id]` | Public published content | Edit/delete controls are conditional on admin state |
| `/notes`, `/notes/[id]` | Public published, non-hidden Note content | Edit/delete/review controls are conditional on admin state |
| `/mistakes` | Public published, non-hidden `Note(type="mistake")` content | Review statistics, review links, diagnosis, and capture links are conditional on admin state |

The public mistake review hooks use a `null` SWR key for anonymous users. Public Note reads are filtered by `status="published"` and `hidden=false` in the backend for non-admin users. No public route is permitted to call admin review, attachment, AI, or capture APIs as part of anonymous rendering.

### Private Manage Contract

| Route family | Classification | Evidence |
|---|---|---|
| `/manage/**` | `active` | `src/app/manage/(workspace)/layout.tsx` wraps the workspace in `AuthGate`; backend admin routers retain `get_current_admin` |
| `/mistakes/review` | `active` | Page-level `AuthGate`; review endpoints retain `get_current_admin` |
| `/write-note` | `preserve` + `active` | Existing protected editor remains a compatibility entry; current links use `/manage/**` |
| `/write-note/[slug]` | `preserve` + `active` | Existing protected editor remains available for historical direct links; current edit links use `/manage/**` |
| `/write-mistake` | `redirect/notice` + `preserve` | Protected compatibility form explicitly directs operators to `/manage/mistakes` and states that old data is not migrated or deleted |
| `/write-mistake/[slug]` | `preserve` + `active` | Existing protected detail/edit entry remains for historical links; no route deletion or data rewrite is allowed |

### Freeze Decisions

1. Do not delete any legacy `/write-*` route solely because `/manage/**` exists.
2. Do not add `AuthGate` to public read routes.
3. Do not expose review metadata, private attachment data, or management controls to anonymous users.
4. Keep backend authorization as the real mutation boundary; frontend gating is only the access-state boundary.
5. If compatibility requires schema or data changes, stop and produce a separate decision report; Batch 7 does not modify schema or data.

## P0-04 Minimal Fix Decision

One existing private workflow state issue was confirmed: `/mistakes/review` left the page in an indefinite loading state when any of its protected review requests failed. The page now stops loading, shows an explicit error, and provides a recovery link to `/manage/mistakes`.

| File | Change | Reason | Impact | Data contract |
|---|---|---|---|---|
| `src/app/mistakes/review/page.tsx` | Add request failure state and recovery UI | Prevent an unbounded loading state on protected review API failure | Private review page only | No |
