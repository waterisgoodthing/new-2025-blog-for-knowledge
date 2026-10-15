# Index Metadata Policy

Date: 2026-07-14
Object: `idx_notes_folder_id`
Mode: policy preparation; index deletion/recreation forbidden.

## Current database role

The database contains a non-unique btree index on `notes(folder_id)`. It supports lookup/filtering for folder-scoped notes and aligns with the nullable `folder_id` relationship to `folders`. Query-plan usage and production workload frequency were not measured in the reviewed read-only pass, so performance criticality remains `UNKNOWN`.

## Migration creation intent

Revision `005` explicitly creates `idx_notes_folder_id` immediately after adding `notes.folder_id`, and its downgrade explicitly drops it. This is positive migration intent and explains why the index is present in the current database history. It does not prove the last physical provisioning event independently of the current revision chain.

## Query path

The reviewed application path filters notes by `Note.folder_id`; `Folder.notes` exposes the relationship. This gives the index a plausible and active query purpose. It does not by itself prove that the current model metadata must express the index.

## SQLAlchemy metadata question

`Note.__table_args__` declares other indexes but omits `idx_notes_folder_id`. The resulting `alembic check` output reports the index as removed from model metadata. This is a real comparison difference, but ownership remains unresolved between intentional historical retention and model metadata omission.

## Policy candidates

### A. Preserve database index, later add model metadata

Keep the current database index and, after owner/query review, add an explicit model declaration in a separately approved implementation. This restores declarative parity and may remove the index drift signal. It requires a model change and verification; neither is authorized now.

### B. Preserve historical index without model expression

Treat the index as an intentionally migration-owned physical optimization that does not need to appear in SQLAlchemy metadata. This would require an explicit policy explaining why autogenerate should not manage it and how future drift checks will protect it.

### C. Other

A different policy could be selected if workload or deployment evidence shows the index should be replaced by another approved access strategy. Such a decision must include query-plan, lock, performance, and rollback analysis.

## Recommendation

Recommend **Candidate A in principle**, with the immediate action limited to **preserve the existing database index**. The model declaration should be considered only after owner approval, query/workload evidence, and a future metadata/migration review. Do not delete, recreate, or alter the index in Phase C+4.

Migration Gate remains `BLOCKED` until the policy is approved and the resulting metadata/migration implications are reviewed.
