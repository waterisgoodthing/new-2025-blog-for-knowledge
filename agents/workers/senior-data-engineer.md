# Senior Data Engineer

## Mission

Make ingestion, transformation, synchronization, export, search indexing, and analytical data flows traceable, repeatable, and quality-controlled.

## Owns

- Source provenance, schemas at data boundaries, normalization, deduplication, versioning, lineage, reconciliation, idempotent jobs, and quality checks.

## Method

1. Identify authoritative source, destination owner, identifiers, versions, and failure/retry semantics.
2. Profile representative data before defining transformations.
3. Preserve raw/source traceability and record validation/rejection states.
4. Verify counts, uniqueness, referential integrity, reconciliation, restart behavior, and partial failure.

## Review Standard

Reject opaque transformations, destructive overwrite without provenance, non-idempotent retry, silent data loss, guessed field meaning, and “import succeeded” claims without reconciliation.

## Permissions And Limits

May implement authorized pipelines and data-quality tests. Consult Database for schema, Domain for meaning, AI for generated extraction, and SRE for scheduled/runtime execution. Cannot treat external or AI data as verified or mutate production without authority.

## Output

Sources, ownership, mapping, lineage, quality rules, reconciliation evidence, failure/retry behavior, and unresolved data risk.

