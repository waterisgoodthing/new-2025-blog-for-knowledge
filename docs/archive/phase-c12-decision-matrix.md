# Phase C+12 Decision Matrix

Date: 2026-07-15
Status: pending governance decisions.

Allowed statuses: `PENDING`, `APPROVED`, `REJECTED`, `DEFERRED`.

| Decision | Option | Recommended | Approver | Status |
|---|---|---|---|---|
| Context Authority | Option A - Complete formal context documents | Preferred if owner/source/version/review/approval can be supplied. | `PENDING` | `PENDING` |
| Context Authority | Option B - Accept waiver | Acceptable only with approver, risk owner, replacement source, accepted risk, and expiry. | `PENDING` | `PENDING` |
| Context Authority | Option C - Pause governance | Use if neither document completion nor waiver is available. | `PENDING` | `PENDING` |
| Ownership Assignment | Assign schema, business, release, migration, and verification owners | Required for any continuation toward Phase D. | `PENDING` | `PENDING` |
| Guest Schema Direction | Option A - Include in future Alembic management | Possible only after provenance, owners, compatibility, retention/privacy, and Alembic ownership are approved. | `PENDING` | `PENDING` |
| Guest Schema Direction | Option B - Keep excluded | Possible only with maintenance responsibility, risk acceptance owner, and future plan. | `PENDING` | `PENDING` |
| Guest Schema Direction | Option C - Enter deprecation process | Possible only with dependency analysis, export plan, retention policy, rollback plan, and removal approval. | `PENDING` | `PENDING` |
| Nullable Contract Direction | Option A - Keep nullable | Possible if owner approves and contract is explicitly confirmed. | `PENDING` | `PENDING` |
| Nullable Contract Direction | Option B - Change to `NOT NULL` | Possible only with business justification, historical analysis, migration impact, and rollback. | `PENDING` | `PENDING` |
| Index Policy | Option A - Sync future ORM metadata | Possible if owner, workload evidence, and query plan support it. | `PENDING` | `PENDING` |
| Index Policy | Option B - Keep database index as governance exception | Possible if exception approval is signed. | `PENDING` | `PENDING` |
| Index Policy | Option C - Delete | Not recommended; currently prohibited. | `PENDING` | `PENDING` |
| Backup/Restore | Provide backup artifact and restore rehearsal | Required before Phase D. | `PENDING` | `PENDING` |
| Deployment | Approve operator, window, rollback, monitoring, escalation, and verification owner | Required before Phase D. | `PENDING` | `PENDING` |

## Matrix Boundary

No row is approved by this matrix. Recommendations are governance guidance only and must not be read as authorization.

```text
Decision Status = PENDING
Migration Gate = BLOCKED
Phase D = NOT AUTHORIZED
```
