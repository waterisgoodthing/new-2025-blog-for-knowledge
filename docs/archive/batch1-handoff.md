# Batch 1 Handoff

## Completed

Batch 1 UI shell now provides:

- `/manage/(workspace)/layout.tsx` protected workspace shell.
- Static `/manage/dashboard`.
- Static containers for required future management areas.
- Sidebar placeholders for Dashboard, Subjects, Knowledge Points, Questions, Mistakes, Review, Attachments, AI, Jobs, Search, Analytics, and Settings.
- Reusable shell components for navigation, topbar, page header, empty state, panel, and status badge.
- Top-level Batch 1 audit, design, validation, and handoff docs.

## Boundaries Preserved

- No database changes.
- No migration.
- No backend changes.
- No API client changes.
- No real Subject, Question, Mistake, Review, Attachment, OCR, Upload, or AI workflow was implemented.
- Existing public pages were not converted into dashboards.

## Important Current-State Note

The worktree contains existing later-batch components and backend/API files from prior work. This pass did not delete them. Instead, current Batch 1 page entries were frozen to static placeholders so the accessible `/manage/**` shell does not call those APIs.

## Batch 2 Entry Needs

Batch 2 Subject / Knowledge Point work can use:

- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`
- Existing shell components:
  - `ManageSidebar`
  - `ManageTopbar`
  - `ManagePageHeader`
  - `ManageEmptyState`
  - `ManagePanel`
  - `ManageStatusBadge`

Before Batch 2 implementation, create or reuse the Batch 2 workflow, update requirements/design/tasks, and get explicit approval for the task list.
