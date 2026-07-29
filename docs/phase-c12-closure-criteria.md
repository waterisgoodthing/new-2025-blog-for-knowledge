# Phase C+12 Closure Criteria

Date: 2026-07-15
Status: criteria only; no closure achieved.

Phase C+12 has two possible exits. Neither exit authorizes implementation unless an explicit later authorization record is created.

## Path A - Continue to Phase D

All of the following must be satisfied:

| Criterion | Required evidence | Current status |
|---|---|---|
| Context resolved | Approved formal context documents or approved waiver with replacement source, risk owner, accepted risk, and expiry. | `BLOCKED` |
| Owners assigned | Named and acknowledged schema owner, business owner, release owner, migration operator, and verification owner. | `BLOCKED` |
| Guest decision completed | Approved choice to include, exclude, or deprecate `guest_messages` and `guest_message_bans`, with required evidence for the chosen option. | `BLOCKED` |
| Contracts approved | Approved nullable contract decision for `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order`. | `BLOCKED` |
| Index policy approved | Approved policy for `idx_notes_folder_id`: metadata sync, governance exception, or separately authorized deletion path. | `BLOCKED` |
| Backup verified | Fresh backup artifact with target identity and timestamp. | `BLOCKED` |
| Restore ready | Isolated restore rehearsal with acceptance result. | `BLOCKED` |
| Rollback ready | Reviewed rollback procedure with named owner and stop/escalation conditions. | `BLOCKED` |
| Deployment approved | Operator, window, monitoring, escalation, and post-change verification owner approved. | `BLOCKED` |
| Authorization signed | Exact files, operations, commands, and limits authorized by the appropriate owner. | `BLOCKED` |

Only after every item is complete may a separate Phase D authorization be considered. Phase C+12 does not create that authorization.

## Path B - Governance Blocked Closure

If the required decisions and evidence cannot be supplied, create a Governance Blocked Closure record.

Minimum contents:

| Closure item | Required content |
|---|---|
| Blocked reason | Identify which required decisions or evidence were not supplied. |
| Scope frozen | State which schema remediation scope is paused. |
| Risk status | State whether risk is unaccepted, accepted with waiver, or deferred. |
| Owner status | State which required roles remain unassigned. |
| Reopen condition | Define what evidence or approval is needed to restart governance. |
| Prohibitions | State that migration generation, migration execution, DDL, DML, database writes, and Phase D remain unauthorized. |

Suggested closure statement:

```text
Governance Blocked Closure

Schema remediation is paused because required governance inputs are incomplete.
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```

## Current Closure State

```text
Closure Path = NOT SELECTED
Decision Status = PENDING
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```
