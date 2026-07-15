# Phase D-2 Model Registry Audit

Date: 2026-07-15
Mode: code implementation audit; no database execution.

## Registry Source

Created:

```text
backend/app/models/registry.py
```

Purpose:

- make Alembic metadata loading explicit and auditable;
- define which SQLAlchemy models are in the schema lifecycle;
- exclude guest schema from Alembic `target_metadata`.

## Included Models

| Model | Included | Reason |
|---|---|---|
| `User` | Yes | Core auth/user table in migration lifecycle. |
| `Tag` | Yes | Core note taxonomy table in migration lifecycle. |
| `Subject` | Yes | Core subject table in migration lifecycle. |
| `Category` | Yes | Core category table in migration lifecycle. |
| `Note` | Yes | Core notes/blog/mistake content table in migration lifecycle. |
| `Folder` | Yes | Folder schema in migration lifecycle; owns `idx_notes_folder_id` relationship context. |
| `MusicItem` | Yes | Music item table in migration lifecycle. |
| `DailyRecommendation` | Yes | Recommendation table in migration lifecycle. |
| `AdminSession` | Yes | Admin session table in migration lifecycle. |
| `PasskeyCredential` | Yes | Passkey credential table in migration lifecycle. |
| `AdminPassword` | Yes | Admin password table in migration lifecycle. |
| `AuditLog` | Yes | Audit log table in migration lifecycle. |
| `NetEaseApiConfig` | Yes | Music daily configuration table in migration lifecycle. |
| `MusicSourceRule` | Yes | Music daily source table in migration lifecycle. |
| `MusicCandidate` | Yes | Music daily candidate table in migration lifecycle. |
| `DailySong` | Yes | Music daily song table in migration lifecycle. |
| `MusicSyncLog` | Yes | Music sync log table in migration lifecycle. |
| `ManagedContentEntry` | Yes | Managed content table in migration lifecycle. |
| `Chapter` | Yes | Taxonomy table in migration lifecycle. |
| `KnowledgePoint` | Yes | Taxonomy table in migration lifecycle. |
| `KnowledgePointLink` | Yes | Taxonomy link table in migration lifecycle. |
| `DraftItem` | Yes | Draft workflow table in migration lifecycle. |
| `QuestionDraft` | Yes | Question draft table in migration lifecycle. |
| `Question` | Yes | Question table in migration lifecycle. |
| `QuestionSource` | Yes | Question source table in migration lifecycle. |
| `MistakeDraft` | Yes | Mistake draft table in migration lifecycle. |
| `Mistake` | Yes | Mistake table in migration lifecycle. |
| `ReviewItem` | Yes | Review item table in migration lifecycle. |
| `ReviewRecord` | Yes | Review record table in migration lifecycle. |
| `Attachment` | Yes | Attachment table in migration lifecycle. |
| `AttachmentLink` | Yes | Attachment link table in migration lifecycle. |
| `CaptureItem` | Yes | Capture item table in migration lifecycle. |
| `AiCallLog` | Yes | AI call log table in migration lifecycle. |
| `AiRun` | Yes | AI run table in migration lifecycle. |
| `GuestMessage` | No | Explicitly excluded by Phase C+13 guest schema decision. |
| `GuestMessageBan` | No | Explicitly excluded by Phase C+13 guest schema decision. |

## Validation Result

Registry import check:

```text
registry_count = 34
has_guest_messages = False
has_guest_message_bans = False
has_notes = True
note_indexes = idx_notes_folder_id, idx_notes_next_review, idx_notes_search, idx_notes_status, ix_notes_slug, ix_notes_type
```

## Boundary

No database command, DDL, DML, Alembic upgrade, or Alembic downgrade was executed.
