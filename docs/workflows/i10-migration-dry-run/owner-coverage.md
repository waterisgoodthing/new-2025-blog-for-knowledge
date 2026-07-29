# I10 Owner Coverage and Conflict Queue

Status: `BLOCKED`

Fresh read-only recheck: 2026-07-26; source counts, revision, user-role split, and empty static indexes are unchanged. The project owner accepted single-owner mode; no canonical target identifier or mapping manifest was supplied.

This is an evidence artifact from the read-only source database at
`localhost:5432/blog_db`, Alembic revision `020`. It does not assign owners or
write either the source or target database.

## Evidence boundary

- The source transaction was opened as `READ ONLY`; `transaction_read_only=on`.
- Source identity was independently rechecked as database `blog_db`, role
  `blog_user`, port `5432`.
- The source has 8 users: 4 administrators and 4 non-administrators.
- An administrator role is not evidence of ownership.
- `created_by` is provenance metadata, not proof of current or target owner.
- `target_type`, `target_id`, slug, path, folder, or a linked note do not prove
  ownership of the linked object.

## Entity coverage

| Source table | Rows | Owner-like fields observed | Evidence-based decision |
| --- | ---: | --- | --- |
| `notes` | 13 | none | `pending_owner_review` |
| `questions` | 3 | none | `pending_owner_review` |
| `mistakes` | 3 | none | `pending_owner_review` |
| `review_items` | 3 | none | `pending_owner_review` |
| `review_records` | 4 | none | `pending_owner_review` |
| `attachments` | 1 | nullable `created_by` only | `pending_owner_review`; provenance is not owner proof |
| `attachment_links` | 1 | none | `pending_owner_review`; linked-object ownership cannot be proven |
| `capture_items` | 0 | nullable `created_by` only | `pending_owner_review`; empty population does not establish a future rule |
| `draft_items` | 6 | nullable `created_by` only | `pending_owner_review`; provenance is not owner proof |
| `ai_runs` | 32 | none | `pending_owner_review`; target relation is insufficient |
| `ai_call_logs` | 47 | none | `pending_owner_review` |
| `users` | 8 | role only; 4 admin / 4 non-admin | not an owner assignment source |

The scan is deliberately conservative: absence of an authoritative owner field
means a row cannot be safely assigned without an external ownership decision.
`attachments.created_by` is retained as provenance evidence only and must not
be silently converted into `owner_id`.

## Conflict queue

The following source populations require an explicit owner/backfill decision
before I11 E-05 can execute:

- 13 notes
- 3 questions
- 3 mistakes
- 3 review items
- 4 review records
- 1 attachment
- 1 attachment link
- 0 capture items
- 6 draft items
- 32 AI runs
- 47 AI call logs

These are queue counts, not new database rows. No source or target database was
written. Until each population has a documented owner rule and a single-owner
approved mapping manifest, the migration gate is `BLOCKED` and the rows remain
outside any shadow migration or authority switch.

## Required decision to unblock

The single project owner must provide a deterministic rule covering the listed
entities, including ambiguous and orphaned rows, and approve the resulting
backfill mapping. The rule must be independently checkable against source
identifiers and must define conflict handling, audit evidence, and rollback
behavior. An administrator default, `created_by` default, or folder default is
not sufficient.
