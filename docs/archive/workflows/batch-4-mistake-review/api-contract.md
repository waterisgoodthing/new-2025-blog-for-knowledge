# API Contract

## Security

All endpoints below are admin-only and must use backend `get_current_admin`. Frontend `AuthGate` protects page experience but is not the security boundary.

## Mistake Draft APIs

```http
GET    /api/admin/mistake-drafts?status=pending
POST   /api/admin/mistake-drafts
GET    /api/admin/mistake-drafts/{draft_item_id}
PUT    /api/admin/mistake-drafts/{draft_item_id}
POST   /api/admin/mistake-drafts/{draft_item_id}/reject
POST   /api/admin/mistake-drafts/{draft_item_id}/convert
```

Create requires exactly one of `question_id` and `question_draft_id`. Reject and convert require the current `version`. Convert returns the formal Mistake and is idempotent for an already converted DraftItem when its target is valid. An inconsistent converted binding returns `409`.

## Mistake APIs

```http
GET    /api/admin/mistakes?status=active
GET    /api/admin/mistakes/{id}
PUT    /api/admin/mistakes/{id}
DELETE /api/admin/mistakes/{id}
```

Delete is archive semantics and requires the current version. A formal Mistake response includes its `review_item_id`.

## Review APIs

```http
GET  /api/admin/review/items?due=true
GET  /api/admin/review/items/{id}/records
POST /api/admin/review/items/{id}/submit
```

Submit request:

```json
{
  "rating": 4,
  "expected_next_review_at": "2026-07-16T00:00:00Z"
}
```

The expected timestamp prevents stale submissions and returns `409` on conflict. Successful submission returns the updated ReviewItem; records remain immutable.

## Error Contract

- `401` unauthenticated;
- `403` authenticated but not admin;
- `404` missing or private resource not visible to caller;
- `409` stale version, inconsistent converted binding, or stale review submission;
- `422` invalid source, state, rating, or Knowledge Point relation.

## Deferred APIs

No Practice, public Mistake, AI, OCR, upload, BKT, analytics, or adaptive scheduling API is introduced by Batch 4.
