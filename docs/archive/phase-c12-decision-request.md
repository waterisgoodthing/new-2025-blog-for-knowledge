# Phase C+12 Governance Decision Request

Date: 2026-07-15
Status: decision request; no approvals recorded.

This document requests governance decisions for blockers that cannot be closed by technical audit alone. It presents choices for the project owner, technical owner, and risk owners. It does not select options, assign owners, create waivers, or authorize Phase D.

## Decision 1 - Context Authority

Current issue: the required formal context documents are missing:

```text
docs/README.md
docs/requirements.md
docs/design.md
```

### Option A - Complete Formal Context

Provide approved context documents with:

| Required item | Status |
|---|---|
| owner | `PENDING` |
| source | `PENDING` |
| version | `PENDING` |
| review | `PENDING` |
| approval | `PENDING` |

Decision effect: governance can continue only after the context set is approved and linked from the migration governance record.

### Option B - Accept Waiver

Approve a formal waiver with:

| Required item | Status |
|---|---|
| approver | `PENDING` |
| risk owner | `PENDING` |
| replacement source | `PENDING` |
| accepted risk | `PENDING` |
| expiry date | `PENDING` |

Decision effect: governance can continue under a time-bounded accepted risk, but the waiver must not be treated as a permanent context replacement unless explicitly renewed.

### Option C - Pause Governance

Pause schema remediation governance until the context authority is supplied or waived.

Decision effect: `Migration Gate = BLOCKED`; `Phase D = NOT AUTHORIZED`.

## Decision 2 - Ownership Assignment

Phase D cannot begin without the following named and acknowledged roles:

| Role | Required decision |
|---|---|
| Schema owner | Name the person accountable for schema authority, drift classification, and migration scope approval. |
| Business owner | Name the person accountable for domain semantics, nullable contracts, guest data meaning, and risk impact. |
| Release owner | Name the person accountable for deployment window, release decision, monitoring, and rollback authorization. |
| Migration operator | Name the person accountable for running approved migration steps and stopping/escalating when conditions fail. |
| Verification owner | Name the person accountable for acceptance criteria, evidence capture, and post-change validation. |

No owner may be inferred from source-code authorship, file ownership, commit history, runtime model presence, or administrator identity.

## Decision 3 - Guest Schema Direction

Objects:

```text
guest_messages
guest_message_bans
```

### Option A - Include in Future Alembic Management

Required before approval:

| Required item | Status |
|---|---|
| creation provenance | `PENDING` |
| schema owner | `PENDING` |
| business owner | `PENDING` |
| compatibility review | `PENDING` |
| retention/privacy decision | `PENDING` |
| Alembic ownership | `PENDING` |

Decision effect: guest schema may become eligible for a future approved migration design, but this option does not itself generate or authorize a migration.

### Option B - Keep Excluded

Required before approval:

| Required item | Status |
|---|---|
| explicit maintenance responsibility | `PENDING` |
| risk acceptance owner | `PENDING` |
| future treatment plan | `PENDING` |

Decision effect: guest schema remains outside the current migration scope under an explicit governance disposition.

### Option C - Enter Deprecation Process

Required before approval:

| Required item | Status |
|---|---|
| dependency analysis | `PENDING` |
| export plan | `PENDING` |
| retention policy | `PENDING` |
| rollback plan | `PENDING` |
| removal approval | `PENDING` |

Decision effect: a separate deprecation workflow may be designed. No deletion, export, retention change, DDL, or DML is authorized by this request.

## Decision 4 - Nullable Contract Direction

Fields:

```text
folders.sort_order
folders.created_at
folders.updated_at
notes.sort_order
```

### Option A - Keep Nullable

Required before approval:

| Required item | Status |
|---|---|
| owner approval | `PENDING` |
| contract confirmation | `PENDING` |

Decision effect: nullable database contract becomes explicit and the model/migration policy must be aligned in a later approved design.

### Option B - Change to NOT NULL

Required before approval:

| Required item | Status |
|---|---|
| business justification | `PENDING` |
| historical analysis | `PENDING` |
| migration impact | `PENDING` |
| rollback | `PENDING` |

Decision effect: a future migration design may be prepared after approval. This request does not authorize constraint changes.

## Decision 5 - Index Policy

Object:

```text
idx_notes_folder_id
```

### Option A - Sync Future ORM Metadata

Required before approval:

| Required item | Status |
|---|---|
| owner | `PENDING` |
| workload evidence | `PENDING` |
| query plan | `PENDING` |

Decision effect: a later approved change may represent the existing index in ORM metadata. This request does not modify models or migrations.

### Option B - Keep Database Index as Governance Exception

Required before approval:

| Required item | Status |
|---|---|
| exception approval | `PENDING` |

Decision effect: the physical index remains intentionally outside ORM metadata under a documented exception.

### Option C - Delete

Current status: prohibited.

Deletion is not available without explicit owner approval, workload/query-plan evidence, migration impact, rollback plan, and a separate execution authorization.

## Requested Governance Response

The governance owner should choose one option for each decision, provide required evidence, and sign or reject the resulting path.

Until that occurs:

```text
Decision Status = PENDING
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```
