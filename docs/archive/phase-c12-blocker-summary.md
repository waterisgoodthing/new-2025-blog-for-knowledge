# Phase C+12 Blocker Summary

Date: 2026-07-15
Mode: governance decision package; documentation only.

Phase C+11 is complete, but blockers remain. This summary escalates unresolved evidence gaps into formal governance decisions. It does not resolve blockers, assign owners, accept risk, authorize Phase D, or approve migration work.

| Category | Current Blocker | Evidence Missing | Risk | Decision Owner |
|---|---|---|---|---|
| Context | The mandatory context set is absent: `docs/README.md`, `docs/requirements.md`, and `docs/design.md` were not supplied, and no qualifying waiver exists. | Approved document owner, source, version, review, approval, or formal waiver with approver, risk owner, replacement source, accepted risk, and expiry. | Schema remediation would proceed without an approved project context baseline, making scope, requirements, and design authority unverifiable. | Context owner, governance sponsor, and risk approver. |
| Ownership | Required roles remain unassigned: schema owner, business owner, release owner, migration operator, and verification owner. | Signed owner assignment and acknowledgement for each role. | No accountable party can approve scope, execution, rollback, verification, or risk acceptance; Phase D cannot be entered. | Governance sponsor and each named owner. |
| Guest Schema | `guest_messages` and `guest_message_bans` are active runtime objects, but physical creation provenance and official schema ownership remain `UNKNOWN`; no Alembic `create_table` record was found. | Creation/provisioning source, schema owner, business owner, compatibility review, retention/privacy decision, and Alembic ownership. | Including the tables could retroactively bless unproven schema; excluding them without a decision could leave active data outside governed migration scope; deleting them is not authorized. | Schema owner, business owner, privacy/risk owner, and Alembic owner. |
| Nullable Contract | `folders.sort_order`, `folders.created_at`, `folders.updated_at`, and `notes.sort_order` remain database/model nullable-contract drift. Interim posture is preservation only, not approval. | Business meaning, owner approval, historical analysis, migration impact, rollback plan, and final choice to keep nullable or change to `NOT NULL`. | A premature constraint change could break legacy/import/write paths; indefinite drift keeps metadata and database authority unresolved. | Schema owner and business owner. |
| Index Policy | `idx_notes_folder_id` exists in the database and migration history but is absent from current ORM metadata; workload and query-plan evidence are missing. | Owner, workload evidence, query plan, migration impact, and explicit policy approval or exception. | Removing the index could harm folder-scoped note queries; adding metadata without approval could mask an unreviewed drift; leaving it unmanaged keeps the governance exception implicit. | Schema owner, notes/domain owner, and performance/release approver. |
| Backup/Restore | No backup artifact, target identity, timestamp, restore rehearsal, or acceptance result was supplied. | Fresh backup evidence, isolated restore validation, schema/revision verification, row/count integrity, attachment validation, and acceptance result. | Any future remediation would lack proven recovery capability and could put production data at unacceptable risk. | Release owner, migration operator, backup/restore owner, and verification owner. |
| Deployment | Deployment operator, execution window, rollback procedure, monitoring, escalation, and post-change verification ownership remain unapproved. | Operator assignment, approved deployment window, rollback procedure, monitoring plan, escalation contact, stop conditions, and verification evidence owner. | Even a technically valid migration would be operationally unauthorizable and unsafe to run. | Release owner, migration operator, verification owner, and governance sponsor. |

## Gate Result

```text
Blocker Status = BLOCKERS_REMAIN
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```

No database changes executed. No migration executed. No production data modified.
