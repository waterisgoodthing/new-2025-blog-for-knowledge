# Schema Coverage Final Matrix

日期：2026-07-14  
链路：SQLAlchemy Model -> `Base.metadata` -> Alembic migration history -> database table。

## Status Rules

- `PASS`: model, runtime metadata, migration create provenance and database table all present.
- `MIGRATION_MISSING`: model/runtime/database present, but migration create provenance absent.
- `MODEL_ONLY`: model/metadata present but database table absent.
- `DATABASE_ONLY`: database table present but model absent.
- `UNKNOWN`: provenance or layer relationship cannot be safely resolved.

## Matrix

| Table | Model | Database | Migration | Status |
|---|---:|---:|---:|---|
| `admin_passwords` | yes | yes | yes (`006`) | PASS |
| `admin_sessions` | yes | yes | yes (`006`) | PASS |
| `ai_call_logs` | yes | yes | yes (`016`) | PASS |
| `ai_runs` | yes | yes | yes (`018`) | PASS |
| `attachment_links` | yes | yes | yes (`014`) | PASS |
| `attachments` | yes | yes | yes (`014`) | PASS |
| `audit_logs` | yes | yes | yes (`008`) | PASS |
| `capture_items` | yes | yes | yes (`015`) | PASS |
| `categories` | yes | yes | yes (`001`) | PASS |
| `chapters` | yes | yes | yes (`011`) | PASS |
| `daily_songs` | yes | yes | yes (`009`) | PASS |
| `draft_items` | yes | yes | yes (`012`) | PASS |
| `folders` | yes | yes | yes (`005`) | PASS with known drift |
| `guest_message_bans` | yes | yes | no record found | MIGRATION_MISSING / provenance UNKNOWN |
| `guest_messages` | yes | yes | no record found | MIGRATION_MISSING / provenance UNKNOWN |
| `knowledge_point_links` | yes | yes | yes (`011`) | PASS |
| `knowledge_points` | yes | yes | yes (`011`) | PASS |
| `managed_content_entries` | yes | yes | yes (`010`) | PASS |
| `mistake_drafts` | yes | yes | yes (`013`) | PASS |
| `mistakes` | yes | yes | yes (`013`) | PASS |
| `music_candidates` | yes | yes | yes (`009`) | PASS |
| `music_items` | yes | yes | yes (`001`) | PASS |
| `music_source_rules` | yes | yes | yes (`009`) | PASS |
| `music_sync_logs` | yes | yes | yes (`009`) | PASS |
| `netease_api_configs` | yes | yes | yes (`009`) | PASS |
| `note_tags` | yes | yes | yes (`001`) | PASS |
| `notes` | yes | yes | yes (`001`,`002`,`003`,`004`,`005`,`1119bee5a419`) | PASS with known drift |
| `passkey_credentials` | yes | yes | yes (`006`) | PASS |
| `question_drafts` | yes | yes | yes (`012`) | PASS |
| `question_sources` | yes | yes | yes (`012`) | PASS |
| `questions` | yes | yes | yes (`012`) | PASS |
| `recommendations` | yes | yes | yes (`001`) | PASS |
| `review_items` | yes | yes | yes (`013`) | PASS |
| `review_records` | yes | yes | yes (`013`) | PASS |
| `subjects` | yes | yes | yes (`001`,`011`) | PASS |
| `tags` | yes | yes | yes (`001`) | PASS |
| `users` | yes | yes | yes (`001`,`0ec85724afb9`) | PASS |
| `alembic_version` | no application model | yes | Alembic bookkeeping | UNKNOWN by application coverage rules |

## Summary

- Runtime model metadata: 37 tables.
- Database public tables: 38, comprising 37 model tables plus `alembic_version`.
- Migration `create_table` inventory: 35 application tables.
- `MIGRATION_MISSING`: `guest_messages`, `guest_message_bans`.
- No `MODEL_ONLY` table observed in the current database.
- No unexplained application `DATABASE_ONLY` table observed; `alembic_version` is expected Alembic bookkeeping, not an application model.

The two guest tables prevent a `PASS` coverage result even though runtime model/database presence matches.

