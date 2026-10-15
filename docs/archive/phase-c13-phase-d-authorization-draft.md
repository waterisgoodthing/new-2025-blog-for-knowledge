# Phase C+13 Phase D Authorization Draft

Date: 2026-07-15
Status: `DRAFT_ONLY`

This draft records the authorization boundary that may be submitted for separate Phase D execution approval. It is not an execution approval and does not authorize implementation.

## Draft Authorization Scope

Phase D may be authorized later to evaluate and implement only the approved future scope:

| Area | Draft scope |
|---|---|
| `backend/main.py` | Remove production `Base.metadata.create_all` dependency and replace it with read-only readiness validation. |
| `backend/alembic/env.py` | Establish deterministic metadata authority and auditable model metadata coverage. |
| Approved model metadata changes | Align only approved metadata direction, including future `idx_notes_folder_id` metadata sync and nullable contract alignment if required by the approved design. |
| Approved migration files | Generate or edit only migrations explicitly approved in the later execution record. |

## Draft Exclusions

The following are excluded from this draft:

```text
guest_messages
guest_message_bans
data cleanup
destructive migration
unapproved nullable changes
index deletion
```

## Required Before Execution

| Requirement | Status |
|---|---|
| Exact file list | `PENDING_EXECUTION_APPROVAL` |
| Exact operation list | `PENDING_EXECUTION_APPROVAL` |
| Backup and restore evidence | `PENDING_EXECUTION_APPROVAL` |
| Rollback plan | `PENDING_EXECUTION_APPROVAL` |
| Validation plan | `PENDING_EXECUTION_APPROVAL` |
| Execution operator | `PENDING_EXECUTION_APPROVAL` |
| Stop conditions | `PENDING_EXECUTION_APPROVAL` |
| Final execution approval | `PENDING_EXECUTION_APPROVAL` |

## Draft Status

```text
Phase D Authorization Draft = CREATED
Phase D Execution Approval = NOT GRANTED
Phase D = AWAITING EXECUTION APPROVAL
```

No database changes executed. No migration executed. No production data modified.
