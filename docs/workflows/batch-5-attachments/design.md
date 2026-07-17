# Domain And UI Design

## Domain Boundary

An Attachment is a private binary plus audit metadata. It is not a Question, Mistake, Note, or AI result. `AttachmentLink` is a generic association record and does not copy domain content into the attachment model.

```text
admin upload -> Attachment(active)
                       |
                 AttachmentLink
                       |
       QuestionDraft / Question / Mistake
```

The attachment remains private even when linked to a domain object. Public publishing is not part of Batch 5.

## Lifecycle

```text
created -> active -> missing
                 -> deleted
```

`deleted` is a soft state. Physical cleanup is deferred. A missing file is detected on access and is not silently recreated. Repeated delete is idempotent and must not rewrite unrelated links.

## Manage Surface

- `/manage/attachments`: dense but readable list, status filter, filename/type/size/date, empty and error states.
- `/manage/attachments/[id]`: metadata, safe preview/download action, status, linked targets, link removal, soft delete.
- Upload is an admin action in the manage surface; no public upload control exists.

Shared API clients remain in `src/lib/api/attachments.ts`; route pages compose existing manage components and do not call APIs directly.

## Security Boundary

`AuthGate` protects the page experience. Every admin attachment API continues to depend on `get_current_admin`. The response never contains `storage_key`, local path, temporary path, or filesystem root.

## Frozen Decisions For Approval

- Keep the current MIME compatibility set: image/png, image/jpeg, image/webp, application/pdf, and text/plain.
- No automatic checksum deduplication; checksum is audit/search preparation only. A repeated upload creates a new attachment unless a later batch defines reuse.
- Deleting an attachment does not cascade-delete links; links remain auditable and become unusable because the attachment is not active.
- No derivative table or thumbnail job in Batch 5; browser preview is limited to supported content types and existing content endpoint behavior.
- Upload uses bounded streaming into a temporary file, calculates SHA-256 while streaming, and atomically finalizes the opaque storage key. Database/file failures use compensating cleanup.
- Client filenames are display metadata only. They cannot determine a storage path; traversal, control characters, empty files, oversize files, and unsupported content are rejected.
- Content access accepts explicit `inline` or `attachment` disposition, rejects symlinked storage paths, and never exposes storage keys or local paths.
- Missing active files transition to `missing` idempotently and return `404`. Soft delete returns `204` for active, missing, and already deleted rows.
- New links allow `source`, `question`, `answer`, and `inline`. Existing `ai_input`/`ai_output` links remain readable; no AI behavior is introduced.
