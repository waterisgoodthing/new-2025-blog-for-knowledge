# Phase C+13 Guest Schema Final Decision

Date: 2026-07-15
Objects: `guest_messages`, `guest_message_bans`

## Decision

```text
Option B - Keep Excluded
Guest Migration Scope = EXCLUDED
```

## Rationale

- The current migration authorization path does not process guest schema.
- Guest physical provenance is not fully confirmed.
- Keeping guest schema excluded avoids expanding the remediation scope.
- Active runtime use does not by itself establish Alembic provenance or authorize retroactive schema ownership.

## Governance Record

| Item | Decision |
|---|---|
| Maintenance responsibility | Project Owner |
| Risk owner | Project Owner |
| Future treatment | Separate governance review |

## Explicit Non-Decisions

This decision is not deletion.

This decision is not deprecation.

This decision is not data cleanup.

This decision does not authorize DDL, DML, migration generation, or modification of `guest_messages` or `guest_message_bans`.

## Result

```text
Guest Migration Scope = EXCLUDED
Guest Schema Future Treatment = SEPARATE_GOVERNANCE_REVIEW
```
