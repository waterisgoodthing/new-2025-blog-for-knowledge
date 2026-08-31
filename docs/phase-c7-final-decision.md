# Phase C+7 Final Decision

Date: 2026-07-14
Status: final pre-implementation review; no implementation approved.

## Guest Schema

| Object | Owner status | Provenance status | Migration eligibility |
|---|---|---|---|
| `guest_messages` | No named approved owner | `UNKNOWN` | `Migration Scope = EXCLUDED` |
| `guest_message_bans` | No named approved owner | `UNKNOWN` | `Migration Scope = EXCLUDED` |

Required before inclusion: physical provenance, named owner, existing data compatibility, retention/privacy decision, and explicit Alembic migration ownership. Active runtime use does not close formal schema ownership.

## Nullable Contracts

| Field | Owner approval | Business contract | Migration allowed? |
|---|---|---|---|
| `folders.sort_order` | No | Not finalized | No; remains `UNKNOWN` |
| `folders.created_at` | No | Not finalized | No; remains `UNKNOWN` |
| `folders.updated_at` | No | Not finalized | No; remains `UNKNOWN` |
| `notes.sort_order` | No | Not finalized | No; remains `UNKNOWN` |

The current zero NULL counts do not establish `NOT NULL` semantics. No nullable migration is approved.

## Index Policy

Object: `idx_notes_folder_id`

- **Candidate A:** preserve database index and later add model metadata declaration after approval.
- **Candidate B:** preserve physical index without ORM metadata expression under an explicit governance exception.
- **Candidate C:** delete index.

Current recommendation remains Candidate A in principle, with only preservation authorized. No model change has been approved and Candidate C is forbidden.

## Final closure status

No guest object is migration-eligible. No nullable change is migration-eligible. No index model change is approved. The unresolved items remain `UNKNOWN` and are not closed by this review.
