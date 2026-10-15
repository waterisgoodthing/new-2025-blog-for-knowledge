# API Contract

All endpoints below are future/implementation contract for the existing admin router. They require `Authorization: Bearer <token>` and backend `get_current_admin`.

## List

`GET /api/admin/attachments?status=active&limit=50&offset=0`

Response (current list contract):

```json
[{"id":"uuid","original_name":"scan.png","mime_type":"image/png","size_bytes":1234,"visibility":"private","status":"active","created_at":"timestamp","updated_at":"timestamp"}]
```

No storage key or local path is returned.

## Upload

`POST /api/admin/attachments` as multipart form data containing `file`.

The server streams within the configured byte bound, calculates SHA-256, validates filename/MIME, writes a temporary file, atomically finalizes it, and returns `201 AttachmentOut`. Empty, oversize, unsupported, unsafe, or failed writes return a documented `4xx/5xx` error without a partial row/file.

## Detail And Content

- `GET /api/admin/attachments/{id}` -> `AttachmentOut`
- `GET /api/admin/attachments/{id}/content?disposition=inline|attachment` -> binary response for active, existing files

Deleted or missing content returns `404`; path containment and symlink checks run before serving; unauthorized access returns `401/403`.

## Delete

`DELETE /api/admin/attachments/{id}` -> `204` for active, missing, or already deleted records. The row is soft-deleted; links are retained for audit.

## Links

- `GET /api/admin/attachments/{id}/links`
- `POST /api/admin/attachment-links`
- `DELETE /api/admin/attachment-links/{link_id}`

Create requires an active attachment, an existing target of an allowed type, and a new-batch purpose of `source`, `question`, `answer`, or `inline`. Existing `ai_input`/`ai_output` rows remain readable but cannot be created by this contract. Exact duplicate returns `409`; deleting a nonexistent link returns `404`. Link output contains target type/id and purpose, never private file paths.

## Error Semantics

`401/403` auth failure; `404` missing resource or unavailable content; `409` duplicate link or state conflict; `413` size limit; `415` unsupported MIME; `422` invalid metadata; `500` storage failure. Error payloads use the existing backend error style.
