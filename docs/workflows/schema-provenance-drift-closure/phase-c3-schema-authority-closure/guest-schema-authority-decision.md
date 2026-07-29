# Guest Schema Authority Decision

Date: 2026-07-14  
Objects: `guest_messages`, `guest_message_bans`  
Mode: design only; no schema change authorized.

## Decision summary

The two tables are active runtime business objects, but their status as formally versioned official schema is **UNKNOWN**. Code presence proves application intent and usage; it does not prove current database provenance or migration authority.

Recommended migration policy: **do not include either table in an executable migration until provenance and ownership are approved.** After approval, the preferred path is Option A, an approved Alembic migration that records the accepted schema as new provenance. Option B, temporary retention, is the current operational state. Option C, deletion, is not supported by current evidence.

## Evidence matrix

| Evidence | Observation | Authority implication |
|---|---|---|
| Model | `backend/app/models/guest_message.py` declares both tables and guest indexes; `models/__init__.py` imports/exports them. | Runtime metadata includes the objects. This is model intent, not physical origin. |
| Router | `backend/app/routers/guest_messages.py` exposes public create/list behavior and admin moderation/ban queries; `backend/main.py` includes the router. | The feature is active and not orphaned. |
| Schema | `backend/app/schemas/guest_message.py` defines create, output, list, and moderation contracts. | API contract exists. It does not establish migration provenance. |
| Migration | Static inventory of `backend/alembic/versions/*` has no `create_table` record for either table. Current revision is `018 (head)`. | Versioned create provenance is missing. |
| Documentation | Prior origin, coverage, and validation reports consistently classify physical origin as `UNKNOWN`; `create_all` is documented as a plausible development path only. | Existing documentation explicitly forbids converting the candidate into a current-database fact. |
| Database SELECT | Both tables exist in `public`; prior read-only counts recorded 8 `guest_messages` rows and 0 `guest_message_bans` rows. | Existence and data impact are known; provisioning path is not. |

## Formal classification

`unknown`

- `official-schema`: not closed because migration provenance and authority are absent.
- `legacy-schema`: not established because no deprecation or retirement evidence exists.
- `orphan-schema`: rejected because model, router, schema, and application registration are active.
- `unknown`: required because current database origin cannot be proven from repository evidence.

## Migration inclusion strategy

### Current state: Option B, temporary retention

Retain both tables and existing data while the decision remains open. This is a preservation posture, not acceptance as official schema and not permission to use startup auto-creation.

Required controls during retention:

- Do not delete, rename, alter, or recreate either table.
- Do not generate or execute a migration that retroactively asserts unproven provenance.
- Do not rely on `Base.metadata.create_all` to provision them in production or as a substitute for migration ownership.
- Treat guest-table writes as existing application behavior whose data impact must be considered before any future change.

### Preferred future state: Option A after approval

If the feature is confirmed as supported business functionality, approve a schema contract, data compatibility review, and explicit Alembic provenance plan. The later migration design must account for the existing tables/data rather than assuming a clean create path. That migration is outside this task and must be independently approved and executed.

### Option C: deletion is not currently eligible

Deletion requires both of the following, neither of which is present:

- deprecation evidence showing the feature is retired and routes/contracts no longer require it;
- data impact analysis covering the 8 existing guest messages, retention/export requirements, and any ban history.

## `create_all` risk

Because the application startup lifecycle invokes `Base.metadata.create_all`, a database missing guest tables could be implicitly provisioned outside Alembic. This creates untracked schema state, makes provenance indistinguishable from external/manual creation, and can cause different environments to have different authority histories. The risk exists even though the current database contains the tables; current existence does not show whether `create_all` created them.

## Required closure evidence

Before classifying the tables as official schema or authorizing Option A, obtain:

1. approved business owner and retention decision;
2. database provisioning history, backup/source snapshot, or equivalent audit evidence;
3. exact current table/index/constraint contract and compatibility review;
4. data impact review for existing messages and bans;
5. explicit approval for a later Alembic provenance migration.

Until those items exist, guest authority remains `UNKNOWN` and Migration Gate remains `BLOCKED`.
