# Schema Design

## Existing Target Schema

### `attachments`

| Column | Type | Constraint / purpose |
|---|---|---|
| `id` | UUID | primary key |
| `original_name` | VARCHAR(255) | required safe display name |
| `storage_provider` | VARCHAR(30) | required, currently `local` only |
| `storage_key` | VARCHAR(255) | required unique opaque key; never returned to clients |
| `mime_type` | VARCHAR(120) | required allowlisted type |
| `size_bytes` | INTEGER | required, `>= 0`, bounded by settings |
| `checksum_sha256` | VARCHAR(64) | required SHA-256 shape |
| `visibility` | VARCHAR(20) | required, currently `private` only |
| `status` | VARCHAR(20) | `active`, `missing`, or `deleted` |
| `created_by` | UUID nullable | FK `users.id`, `ON DELETE SET NULL`; audit metadata only |
| `created_at`, `updated_at` | timestamp | required audit timestamps |
| `deleted_at` | timestamp nullable | soft-delete timestamp |

Indexes cover checksum, `(status, created_at)`, and unique storage key.

### `attachment_links`

| Column | Type | Constraint / purpose |
|---|---|---|
| `id` | UUID | primary key |
| `attachment_id` | UUID | FK `attachments.id`, `ON DELETE CASCADE` |
| `target_type` | VARCHAR(30) | `question_draft`, `question`, or `mistake` |
| `target_id` | VARCHAR(64) | target identifier; string-compatible contract |
| `purpose` | VARCHAR(30) | source/question/answer/inline/ai_input/ai_output |
| `sort_order` | INTEGER | stable presentation order |
| `created_at` | timestamp | audit timestamp |

Unique key: `(attachment_id, target_type, target_id, purpose)`. Indexes cover attachment and target lookup.

## Migration Position

Current database is `020 (head)` and the audited tables match the current model/migration shape. No migration is planned for Batch 5. Any implementation-discovered drift must stop the task and require a new approval before migration work.

## Data Preservation

Never rebuild, truncate, re-key, bulk rewrite, or silently migrate attachment/link rows. Existing links to `mistake` remain valid under the current contract.
