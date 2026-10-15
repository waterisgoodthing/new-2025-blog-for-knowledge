# Phase D Stop Conditions

Date: 2026-07-15
Status: stop-condition definition; no execution.

Execution must stop immediately if any of the following occur:

| Stop condition | Required action |
|---|---|
| Backup unavailable | Do not start execution. Obtain backup and restore evidence first. |
| Restore verification unavailable | Do not start execution. Complete isolated restore rehearsal first. |
| Migration SQL unexpected | Stop before execution. Review SQL and update approval if scope changes. |
| Unauthorized object included | Stop before execution. Remove object from plan or obtain separate governance approval. |
| Schema drift detected | Stop and classify drift before generating or executing migration. |
| Rollback unavailable | Do not start execution. Approve rollback method and owner first. |
| Validation failure | Stop, preserve evidence, and follow rollback/escalation procedure. |
| `guest_messages` or `guest_message_bans` included | Stop. Guest schema is explicitly excluded. |
| Destructive operation detected | Stop. Destructive migration is excluded. |
| Unapproved nullable change detected | Stop. Nullable contract is `APPROVED_KEEP_NULLABLE`. |
| Index deletion detected | Stop. `idx_notes_folder_id` deletion is not authorized. |

## Current Status

```text
Stop Conditions = DEFINED
Execution Authorization = NOT APPROVED
Implementation = NOT STARTED
```
