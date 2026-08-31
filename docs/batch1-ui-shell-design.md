# Batch 1 UI Shell Design

## Page Structure

`/manage` remains the legacy login and old management entry. The new management workspace lives under the route group:

```text
src/app/manage/(workspace)/
  layout.tsx
  dashboard/page.tsx
  subjects/page.tsx
  knowledge-points/page.tsx
  questions/page.tsx
  mistakes/page.tsx
  review/page.tsx
  attachments/page.tsx
  ai/page.tsx
  jobs/page.tsx
  search/page.tsx
  analytics/page.tsx
  settings/page.tsx
```

`layout.tsx` wraps workspace pages in `AuthGate`, `ManageSidebar`, `ManageMobileNav`, `ManageTopbar`, and a content area.

## Component Structure

Batch 1 shell components:

- `ManageSidebar`: static navigation only.
- `ManageTopbar`: compact workspace header and public-home return link.
- `ManagePageHeader`: consistent title, eyebrow, and description.
- `ManagePlaceholderPage`: reusable static placeholder for future batches.
- `ManageEmptyState`, `ManagePanel`, `ManageStatusBadge`: foundation components without business interpretation.

No component in the Batch 1 page path owns Subject, Question, Mistake, Review, Attachment, AI, OCR, or Upload business logic.

## Route Design

Sidebar placeholders:

- Dashboard
- Subjects
- Knowledge Points
- Questions
- Mistakes
- Review
- Attachments
- AI
- Jobs
- Search
- Analytics
- Settings

Dashboard is a static "Learning Workspace / Coming Soon" entry page. It links to static containers and shows no real counts.

## Visual Separation

Public layer:

- Low density.
- Existing soft blue-green, glass-card, youthful visual language.
- Homepage remains a public reading surface with a light learning entry.

Manage layer:

- Higher information density.
- Sidebar + topbar + header + content area.
- Clear hierarchy, keyboard focus states, empty states, and static placeholders.
- No table, filter, or real operational workflow is enabled in Batch 1.

## Authentication Boundary

`AuthGate` is used only for page access experience under `/manage/**`.

Frontend protection is not a security boundary. Future backend admin APIs must enforce real security for write, upload, AI, review, and learning data operations.

## Explicit Non-Goals

- No database change.
- No migration.
- No real CRUD.
- No real learning workflow.
- No Subject, Question, Mistake, Review, Attachment, OCR, Upload, or AI integration.
- No fake statistics.
- No homepage dashboard conversion.
