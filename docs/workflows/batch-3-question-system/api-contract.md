# API Contract

## Scope

This file defines future API contracts only. It does not implement routes.

All endpoints are admin-only:

```text
/api/admin/questions
```

No public Question API is introduced in Batch 3.

The direct Question API is the canonical new write/read contract. Existing Draft endpoints remain available only for compatibility with current data and downstream workflows; they are not part of the Batch 3 API expansion.

## Security Boundary

Every endpoint requires backend admin authentication.

Expected responses:

- `401` unauthenticated
- `403` authenticated but not admin
- `404` not found
- `409` version conflict or domain conflict
- `422` invalid payload

Frontend AuthGate is not the security boundary.

## Types

### Question Type

```json
["single_choice", "multiple_choice", "true_false", "short_answer", "essay"]
```

### Difficulty

```json
["unspecified", "easy", "medium", "hard"]
```

### Question Status

```json
["active", "archived"]
```

## GET Question List

```http
GET /api/admin/questions?subject_id=1&knowledge_point_id=10&type=single_choice&difficulty=easy&status=active
```

Response:

```json
{
  "items": [
    {
      "id": "uuid",
      "subject_id": 1,
      "title": "三角函数基础题",
      "stem_md": "已知 ...",
      "question_type": "single_choice",
      "difficulty": "easy",
      "status": "active",
      "knowledge_point_ids": [10, 12],
      "updated_at": "2026-07-15T00:00:00Z"
    }
  ]
}
```

List responses may omit full `answer_data` and `analysis_md` if the UI does not need them.

## GET Question Detail

```http
GET /api/admin/questions/{id}
```

Response:

```json
{
  "id": "uuid",
  "subject_id": 1,
  "title": "三角函数基础题",
  "stem_md": "已知 ...",
  "question_type": "single_choice",
  "options": [
    { "key": "A", "text": "..." },
    { "key": "B", "text": "..." }
  ],
  "answer_data": {
    "kind": "single_choice",
    "value": ["A"]
  },
  "analysis_md": "解析 Markdown",
  "difficulty": "easy",
  "status": "active",
  "visibility": "private",
  "version": 1,
  "knowledge_points": [
    {
      "id": 10,
      "name": "三角函数",
      "role": "primary",
      "sort_order": 0
    }
  ],
  "sources": [
    {
      "id": "uuid",
      "source_type": "manual",
      "source_title": "手工录入",
      "source_ref": null,
      "source_url": null,
      "source_note": null
    }
  ],
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

## POST Question

```http
POST /api/admin/questions
```

Request:

```json
{
  "subject_id": 1,
  "title": "三角函数基础题",
  "stem_md": "已知 ...",
  "question_type": "single_choice",
  "options": [
    { "key": "A", "text": "..." },
    { "key": "B", "text": "..." }
  ],
  "answer_data": {
    "kind": "single_choice",
    "value": ["A"]
  },
  "analysis_md": "解析 Markdown",
  "difficulty": "easy",
  "knowledge_point_links": [
    { "knowledge_point_id": 10, "role": "primary", "sort_order": 0 }
  ],
  "sources": [
    {
      "source_type": "manual",
      "source_title": "手工录入"
    }
  ]
}
```

Response: Question detail.

## PATCH Question

```http
PATCH /api/admin/questions/{id}
```

Request fields are partial and must include the current version:

```json
{
  "version": 1,
  "difficulty": "medium",
  "analysis_md": "更新后的解析"
}
```

Response: Question detail with incremented version.

## POST Archive Question

```http
POST /api/admin/questions/{id}/archive
```

Request:

```json
{
  "version": 2
}
```

Response: archived Question detail.

## Relation Validation

For create/update:

- `subject_id` must exist.
- all `knowledge_point_id` values must exist.
- every Knowledge Point must belong to the Question Subject.
- archived Knowledge Points are rejected by default.
- duplicate Knowledge Point IDs are rejected.

## Source Validation

For create/update:

- at least one source is recommended, defaulting to `manual`.
- `source_type = url` requires `source_url`.
- future `ai`, `ocr`, `capture`, or `import` source types require separate approval.

## Deferred API

Not in Batch 3:

- `/api/admin/question-drafts`
- `/api/admin/practice-*`
- `/api/admin/mistakes`
- `/api/public/questions`
- bulk import
- AI question generation
- OCR question extraction

## Compatibility API Boundary

The following existing capabilities must not be removed by the Batch 3 implementation until their consumers are migrated and verified:

- existing Question list/detail/update/archive reads;
- QuestionDraft creation, update, conversion, and rejection;
- DraftItem conversion records used by Mistake and AI flows.

The compatibility boundary does not authorize new Draft, Mistake, Capture, Attachment, or AI behavior. It only prevents the direct Question API from breaking existing persisted data and callers.
