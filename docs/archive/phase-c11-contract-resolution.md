# Phase C+11 Contract Resolution

Date: 2026-07-15

| Field | Owner | Business meaning | Historical analysis | Migration impact | Result |
|---|---|---|---|---|---|
| `folders.sort_order` | Unassigned | Folder ordering; active ordering path is evidenced | DB nullable with default `0`; prior NULL `0/2`; zero NULLs do not prove non-null intent | A constraint change could reject legacy/import writes and needs rollback | `BLOCKED` |
| `folders.created_at` | Unassigned | Folder creation timestamp | DB nullable with `now()` default; prior NULL `0/2`; import/lifecycle contract not approved | Constraint change could affect legacy/import data and write paths | `BLOCKED` |
| `folders.updated_at` | Unassigned | Folder update timestamp | DB nullable with `now()` default; prior NULL `0/2`; ORM update behavior is not a business approval | Constraint change could affect partial or historical writes | `BLOCKED` |
| `notes.sort_order` | Unassigned | Note ordering; active ordering path is evidenced | DB nullable with default `0`; prior NULL `0/13`; zero NULLs do not prove non-null intent | Constraint change could reject legacy/import writes and needs rollback | `BLOCKED` |

## Contract Boundary

The interim preservation policy is `KEEP NULLABLE` for all four fields. It is a risk-containment observation, not an approved ORM or database change. `APPROVED_KEEP_NULLABLE` or `APPROVED_NOT_NULL` cannot be issued without a named owner, business justification, historical analysis beyond the current NULL count, migration impact, rollback, and approval evidence.

No nullable migration is eligible.
