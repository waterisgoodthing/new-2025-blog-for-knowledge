# Phase C+10 Contract Evidence

Date: 2026-07-15
Status: blocked; no nullable contract approved.

| Field | Business Owner | Contract | Evidence | Status |
|---|---|---|---|---|
| `folders.sort_order` | Unassigned | Interim `KEEP NULLABLE`; final contract `UNKNOWN` | DB nullable `YES`, default `0`, prior NULL `0/2`; active folder ordering path; no owner/business approval | `BLOCKED` |
| `folders.created_at` | Unassigned | Interim `KEEP NULLABLE`; final contract `UNKNOWN` | DB nullable `YES`, default `now()`, prior NULL `0/2`; ORM non-null timestamp; no lifecycle/import approval | `BLOCKED` |
| `folders.updated_at` | Unassigned | Interim `KEEP NULLABLE`; final contract `UNKNOWN` | DB nullable `YES`, default `now()`, prior NULL `0/2`; ORM `onupdate`; no owner/update contract approval | `BLOCKED` |
| `notes.sort_order` | Unassigned | Interim `KEEP NULLABLE`; final contract `UNKNOWN` | DB nullable `YES`, default `0`, prior NULL `0/13`; active note ordering path; no owner approval | `BLOCKED` |

## Accepted contract choices

The only safe interim choice is `KEEP NULLABLE`, preserving the current physical database contract while evidence is incomplete. This does not authorize ORM changes or a database constraint change.

`CHANGE TO NOT NULL` would require a business reason, historical analysis beyond current NULL counts, migration impact, rollback plan, owner approval, and verification evidence. None is available.

## Conclusion

Contract evidence is `BLOCKED`; no nullable migration is eligible.
