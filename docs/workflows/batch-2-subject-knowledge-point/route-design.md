# Route Design

## Scope

This route design uses the Batch 1 management shell. It does not modify route files in this design round.

Routes:

- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`

All routes are private management routes under the Batch 1 `AuthGate` workspace. Frontend protection is page-access experience only; backend admin API authentication remains the real security boundary.

## `/manage/subjects`

### Responsibility

Subject list and top-level management.

Future page responsibilities:

- Show all Subjects.
- Filter by status: active / archived / all.
- Show count of direct root Knowledge Points only if supported by Subject API or tree summary.
- Provide entry to create Subject after implementation is approved.
- Link to `/manage/subjects/[id]`.

### Data Source

Future:

```text
GET /api/admin/subjects
```

or the repository's approved admin namespace equivalent.

Current Batch 2 design round:

```text
No data source connected.
```

### States

Future page must support:

- loading
- empty
- filtered empty
- error
- archived subject display
- dependency conflict when delete is later implemented

## `/manage/subjects/[id]`

### Responsibility

Subject detail and its Knowledge Point tree overview.

Future page responsibilities:

- Show Subject identity, status, description, and sort order.
- Show root Knowledge Points for the Subject.
- Show tree preview or nested list.
- Link to Knowledge Point detail pages.
- Provide edit/archive actions after implementation approval.

### Data Source

Future:

```text
GET /api/admin/subjects/{id}
GET /api/admin/subjects/{id}/knowledge-tree
```

Current Batch 2 design round:

```text
No data source connected.
```

### Extension Direction

Later batches may show related Questions, Mistakes, and Review summaries, but Batch 2 must not design or implement those panels beyond placeholder slots.

## `/manage/knowledge-points`

### Responsibility

Cross-subject Knowledge Point browsing and tree entry.

Future page responsibilities:

- Select a Subject.
- Display its Knowledge Point tree.
- Support expand/collapse.
- Support tree ordering after implementation approval.
- Link to `/manage/knowledge-points/[id]`.

### Data Source

Future:

```text
GET /api/admin/knowledge-points/tree?subject_id={id}
```

or:

```text
GET /api/admin/subjects/{id}/knowledge-tree
```

Current Batch 2 design round:

```text
No data source connected.
```

### Extension Direction

Future mind-map display can use the same tree response. Batch 2 must not implement visualization.

## `/manage/knowledge-points/[id]`

### Responsibility

Knowledge Point detail page.

Future page responsibilities:

- Show node identity, Subject, parent, path, status, sort order, and description.
- Show children list.
- Show future reference sections as disabled/placeholder only until their batches.
- Provide move/archive/edit actions after implementation approval.

### Data Source

Future:

```text
GET /api/admin/knowledge-points/{id}
GET /api/admin/knowledge-points/{id}/children
GET /api/admin/knowledge-points/{id}/path
```

Current Batch 2 design round:

```text
No data source connected.
```

## Public Routes

No public route changes.

The public layer remains:

- low-density
- readable
- not a dashboard
- free of private taxonomy management controls

## Route Compatibility With Batch 1

Batch 1 created the shell and placeholders. Batch 2 implementation may replace only the Subject and Knowledge Point placeholder page content after approval. It must not change:

- `/manage` root legacy login/management behavior
- global homepage layout
- unrelated placeholders for Questions, Mistakes, Review, Attachments, AI, Jobs, Search, Analytics, Settings
