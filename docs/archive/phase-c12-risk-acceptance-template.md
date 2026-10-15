# Phase C+12 Risk Acceptance Template

Date: 2026-07-15
Purpose: template for formal risk acceptance only.

This template is intentionally blank. It must not be treated as approval until an authorized approver, risk owner, scope, expiry, and accepted impact are supplied.

| Risk | Impact | Scope | Owner | Accepted By | Expiry |
|---|---|---|---|---|---|
| Context authority waiver |  |  |  |  |  |
| Unassigned ownership |  |  |  |  |  |
| Guest schema provenance remains `UNKNOWN` |  |  |  |  |  |
| Guest schema excluded from migration scope |  |  |  |  |  |
| Nullable contract remains drifted |  |  |  |  |  |
| `idx_notes_folder_id` remains a metadata exception |  |  |  |  |  |
| Backup/restore evidence missing |  |  |  |  |  |
| Deployment and rollback evidence missing |  |  |  |  |  |

## Required Acceptance Rules

- `Owner` must be the accountable risk owner, not an inferred code author.
- `Accepted By` must be an authorized approver.
- `Scope` must identify exactly what is accepted and what remains blocked.
- `Expiry` is required for every waiver or temporary acceptance.
- Risk acceptance does not authorize DDL, DML, migration generation, migration execution, or Phase D unless a separate authorization record explicitly does so.

## Current Status

```text
Risk Acceptance = NOT APPROVED
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```
