# Requirements

## In Scope

1. Admin-only local attachment upload with bounded size and allowlisted MIME types.
2. Private metadata list/detail views under `/manage/attachments`.
3. Admin-only content preview/download without exposing storage paths or keys.
4. Soft deletion with explicit status handling.
5. Generic links to existing `question_draft`, `question`, and `mistake` targets.
6. Filename safety, checksum calculation, path containment, missing-file detection, and useful empty/error states.

## Compatibility

- Existing `attachments` and `attachment_links` rows are data-bearing and must remain readable.
- Existing `text/plain` data is preserved; the implementation must not narrow the allowlist in a way that makes it inaccessible.
- `created_by` remains nullable compatibility metadata in the current single-admin model. It is not an ownership or multi-tenant boundary.
- No migration is authorized unless schema reconciliation proves an additive, reversible change is necessary.

## Explicitly Out Of Scope

OCR, Capture, AI input/output execution, automatic PDF extraction, thumbnails/derivative generation, object storage, public URLs, bulk import, deduplication/reuse workflow, Practice, Search, Analytics, and new attachment target domains.

## Acceptance Requirements

- `/manage/attachments` and `/manage/attachments/[id]` are admin-protected.
- Attachment mutation and content endpoints use backend admin authorization.
- Deleted or missing attachments cannot be served as active content.
- Links validate active attachment and existing target, and duplicate links return a documented conflict.
- No existing attachment/link/Question/Mistake/Note data is rewritten or deleted by the implementation.
