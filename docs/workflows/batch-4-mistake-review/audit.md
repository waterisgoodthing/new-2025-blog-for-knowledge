# Audit

## Status

P0-01 current-state audit completed read-only. No Batch 4 code or migration changes were made while preparing this workflow.

## Database Evidence

Active Alembic revision:

```text
020 (head)
```

Current row counts:

| Table | Rows | Classification |
|---|---:|---|
| `mistake_drafts` | 3 | data-bearing private draft stack |
| `mistakes` | 3 | data-bearing private formal stack |
| `review_items` | 3 | data-bearing review schedule stack |
| `review_records` | 4 | data-bearing immutable history |
| `notes` | 13 | existing public/private Note system, including legacy mistake records |

## Schema Lineage Reconciliation

The implementation lineage is `013 -> ... -> 018 -> 019 -> 020` with current revision `020`.

- `013` creates the data-bearing MistakeDraft, Mistake, ReviewItem, and ReviewRecord tables and expands shared DraftItem constraints.
- `019` changes the Subject/Knowledge Point taxonomy and is outside the Mistake table lineage, but its current revision must be included in all migration checks.
- `020` adds canonical Question fields and the dedicated Question relation while preserving the generic Mistake relation and legacy Question fields.

P0-04 must compare the actual database against all applied revisions through `020`; a comparison limited to `013-018` is insufficient.

## Existing Code

Existing backend artifacts include:

- `MistakeDraft`, `Mistake`, `ReviewItem`, `ReviewRecord` models;
- admin draft, mistake, and review-item routers;
- `mistake_service`, `review_item_service`, and fixed-interval review logic;
- route contract tests and service tests;
- frontend Mistake API client and older Note-backed Review API client.

## Dependency Findings

- `MistakeDraft` can source a formal Question or QuestionDraft.
- QuestionDraft sources require conversion before Mistake conversion.
- Mistake conversion creates one ReviewItem and is tested for idempotency.
- Archiving a Mistake pauses its ReviewItem.
- Generic `knowledge_point_links` remains the Mistake/MistakeDraft relation.
- Existing `/api/review/*` operates on `Note(type="mistake")`; it must not be silently relabeled as the new private ReviewItem API.
- Existing public `/mistakes` behavior remains governed by the Note permission boundary.

## Risks

- The repository has two review paths: old Note-backed `/api/review/*` and new admin ReviewItem APIs.
- Existing models are already data-bearing, so replacement migrations would be destructive without mapping.
- Batch 3 changed canonical Question fields while preserving legacy Question fields; Mistake snapshots must continue to work with both.
- Batch 2 taxonomy metadata drift remains a known Alembic check gap.

## P0-01 Conclusion

Batch 4 is not a blank implementation. The safe implementation path is a compatibility audit and targeted hardening of the existing private Mistake/Review stack, while keeping public Note mistakes unchanged.
