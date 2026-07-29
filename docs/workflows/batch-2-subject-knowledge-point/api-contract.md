# API Contract

## Scope

This file defines future API contracts only. It does not implement backend routes, schemas, services, or frontend clients.

All APIs are admin/private APIs. Exact prefix must be confirmed during implementation because current architecture targets `/api/admin/**`, while existing repository routes may have historical paths.

Design preference:

```text
/api/admin/subjects
/api/admin/knowledge-points
```

## Security Boundary

Every endpoint requires backend admin authentication.

Frontend `AuthGate` is not a security boundary.

Expected error boundary:

- `401` unauthenticated
- `403` authenticated but not admin

## Subject Contracts

### GET Subject List

```http
GET /api/admin/subjects?status=active|archived|all
```

Request query:

| Field | Type | Required | Notes |
| --- | --- | ---: | --- |
| `status` | string | no | Defaults to `active` |

Response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "数学",
      "description": "数学学习轨道",
      "status": "active",
      "sort_order": 10,
      "created_at": "2026-07-15T00:00:00Z",
      "updated_at": "2026-07-15T00:00:00Z"
    }
  ]
}
```

### GET Subject Detail

```http
GET /api/admin/subjects/{id}
```

Response:

```json
{
  "id": 1,
  "name": "数学",
  "description": "数学学习轨道",
  "status": "active",
  "sort_order": 10,
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

### POST Subject

```http
POST /api/admin/subjects
```

Request:

```json
{
  "name": "数学",
  "description": "数学学习轨道",
  "sort_order": 10
}
```

Response:

```json
{
  "id": 1,
  "name": "数学",
  "description": "数学学习轨道",
  "status": "active",
  "sort_order": 10,
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

### PATCH Subject

```http
PATCH /api/admin/subjects/{id}
```

Request fields are partial:

```json
{
  "name": "数学",
  "description": "更新说明",
  "status": "archived",
  "sort_order": 20
}
```

### DELETE Or Archive Subject

Design preference:

```http
PATCH /api/admin/subjects/{id}
```

with:

```json
{
  "status": "archived"
}
```

Hard delete, if added later, must reject when dependent Knowledge Points exist.

## Knowledge Point Contracts

### GET Knowledge Tree

```http
GET /api/admin/subjects/{subject_id}/knowledge-tree?status=active|archived|all
```

Response:

```json
{
  "subject": {
    "id": 1,
    "name": "数学"
  },
  "nodes": [
    {
      "id": 10,
      "subject_id": 1,
      "parent_id": null,
      "name": "高等数学",
      "description": null,
      "status": "active",
      "sort_order": 10,
      "children": [
        {
          "id": 11,
          "subject_id": 1,
          "parent_id": 10,
          "name": "函数",
          "description": null,
          "status": "active",
          "sort_order": 10,
          "children": []
        }
      ]
    }
  ]
}
```

Default response is a nested tree.

Flat node queries remain supported separately for:

- backend editing
- large tree loading
- move validation
- recursive calculations
- future search indexing

### GET Knowledge Point List

```http
GET /api/admin/knowledge-points?subject_id=1&parent_id=10&status=active
```

Request query:

| Field | Type | Required | Notes |
| --- | --- | ---: | --- |
| `subject_id` | integer | no | Required for tree screens |
| `parent_id` | integer/null | no | Direct children |
| `status` | string | no | Defaults to active |

Response:

```json
{
  "items": [
    {
      "id": 11,
      "subject_id": 1,
      "parent_id": 10,
      "name": "函数",
      "description": null,
      "status": "active",
      "sort_order": 10,
      "created_at": "2026-07-15T00:00:00Z",
      "updated_at": "2026-07-15T00:00:00Z"
    }
  ]
}
```

### GET Knowledge Point Detail

```http
GET /api/admin/knowledge-points/{id}
```

Response:

```json
{
  "id": 11,
  "subject_id": 1,
  "parent_id": 10,
  "name": "函数",
  "description": null,
  "status": "active",
  "sort_order": 10,
  "path": [
    { "id": 10, "name": "高等数学" },
    { "id": 11, "name": "函数" }
  ],
  "children_count": 1,
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

### POST Knowledge Point

```http
POST /api/admin/knowledge-points
```

Request:

```json
{
  "subject_id": 1,
  "parent_id": 10,
  "name": "三角函数",
  "description": null,
  "sort_order": 20
}
```

Rules:

- `subject_id` must exist.
- `parent_id`, if present, must exist.
- Parent must belong to the same Subject.
- Sibling duplicate names are rejected.

### PATCH Knowledge Point

```http
PATCH /api/admin/knowledge-points/{id}
```

Request fields are partial:

```json
{
  "parent_id": 10,
  "name": "三角函数",
  "description": "更新说明",
  "status": "active",
  "sort_order": 30
}
```

Rules:

- Cannot set parent to self.
- Cannot set parent to descendant.
- Cannot move under a parent from another Subject.

### Archive Knowledge Point

Design preference:

```http
PATCH /api/admin/knowledge-points/{id}
```

with:

```json
{
  "status": "archived"
}
```

Archive recursively applies to the full subtree.

Service requirement:

- set selected node to `archived`
- recursively set all descendants to `archived`
- preserve parent-child relationships
- do not delete nodes

## Error Contract

| Status | Meaning |
| ---: | --- |
| 400 | invalid parent relation, cycle attempt, parent from another Subject |
| 401 | unauthenticated |
| 403 | authenticated but not admin |
| 404 | Subject or Knowledge Point not found |
| 409 | duplicate name or dependency conflict |
| 422 | field validation failure |

## Forbidden API Scope In Batch 2

Do not define or implement:

- Question binding endpoints
- Mistake binding endpoints
- Review endpoints
- Attachment upload endpoints
- AI suggestion endpoints
- Search or analytics endpoints
