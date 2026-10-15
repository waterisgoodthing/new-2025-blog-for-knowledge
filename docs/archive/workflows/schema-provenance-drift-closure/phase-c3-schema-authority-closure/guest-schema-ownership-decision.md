# Guest Schema Ownership Decision

Date: 2026-07-14  
Objects: `guest_messages`, `guest_message_bans`  
Formal classification: `unknown`

## Question 1: Are these official schema?

Not closed as `official-schema`. The tables are active application-domain objects, but formal schema authority and physical provenance are not established. `legacy-schema` is also not proven because no deprecation or retirement record exists. `orphan-schema` is rejected because active runtime references exist.

## Evidence

| Evidence area | Finding |
|---|---|
| Model evidence | `backend/app/models/guest_message.py:11-42` declares both tables in `Base.metadata`; guest message indexes are also declared. `backend/app/models/__init__.py` exports both models. |
| Router evidence | `backend/app/routers/guest_messages.py:19` registers `/api/guest-messages`; create/list, moderation, rate-limit, and ban queries use both models. `backend/main.py:96` includes the router. |
| Schema evidence | `backend/app/schemas/guest_message.py:7-34` defines create, output, list, and moderation contracts. |
| Migration evidence | Static inspection of `backend/alembic/versions/*` found no `create_table` operation for either guest table. Current Alembic revision is `018 (head)`. |
| Documentation evidence | Existing Phase C reports record missing migration provenance and the startup `create_all` candidate, but explicitly keep physical origin `UNKNOWN`. No deprecation/removal evidence was found. |
| Database evidence | Read-only SELECT found both tables. `guest_messages` has 8 rows and `guest_message_bans` has 0 rows. Existence does not prove provisioning origin. |

## Provenance classification

`unknown`. The strongest repository candidate is development-time `Base.metadata.create_all`, but that is not evidence of how the current database was provisioned. Manual DDL, external provisioning, or an omitted historical migration remain unproven.

## Question 2: Future schema authority

### Recommended disposition

Operationally choose **Option B: retain temporarily as legacy-candidate objects**, while keeping the formal classification `unknown`. Preserve both tables and their data during this decision phase. Do not delete, alter, or retroactively claim migration provenance.

The exit decision for the retained state is a human-approved choice between:

- **Option A:** accept the guest feature as official schema and generate an approved Alembic migration provenance plan after schema/data review; or
- **Option C:** deprecate and delete only after explicit deprecation evidence and data impact analysis.

Option C is not currently supportable: the feature is active, `guest_messages` contains data, and no deprecation or retention/export decision exists.

## Gate implication

Guest-table provenance and official ownership remain unresolved. The tables must not be included in an executable migration scope in this phase. Migration Gate remains `BLOCKED`.
