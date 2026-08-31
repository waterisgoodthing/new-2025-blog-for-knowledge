# Column Drift Ownership Report

日期：2026-07-14  
对象：`folders.sort_order`、`folders.created_at`、`folders.updated_at`、`notes.sort_order`。  
Allowed classifications only: `database drift`, `model drift`, `migration omission`, `metadata registration issue`, `unknown`.

## Evidence Table

| Field | Database | Model | Migration | Classification | Evidence |
|---|---|---|---|---|---|
| `folders.sort_order` | integer; nullable YES; default `0`; NULL count `0/2` | `Integer`; `nullable=False`; Python default `0`; no server default | revision `005` creates integer, omits nullable, server default `0` | `unknown` | type/default compatible; nullable intent differs; no approved semantic decision |
| `folders.created_at` | timestamp without time zone; nullable YES; default `now()`; NULL count `0/2` | `DateTime`; `nullable=False`; server default `now()` | revision `005` creates DateTime, omits nullable, server default `now()` | `unknown` | database has no current NULL rows, but historical/model intent is not enough to assign ownership |
| `folders.updated_at` | timestamp without time zone; nullable YES; default `now()`; NULL count `0/2` | `DateTime`; `nullable=False`; server default `now()` | revision `005` creates DateTime, omits nullable, server default `now()` | `unknown` | nullable differs; update semantics and historical intent require approval |
| `notes.sort_order` | integer; nullable YES; default `0`; NULL count `0/13` | `Integer`; `nullable=False`; Python default `0`; no server default | revision `005` adds integer, omits nullable, server default `0` | `unknown` | type/default compatible; nullable intent differs; no approved semantic decision |

## Interpretation

All four database columns currently have zero NULL rows. This reduces immediate data cleanup risk but does not resolve authority: a nullable column with no NULL values is still structurally different from a non-null model declaration.

The migration uses omitted `nullable` for these fields, which allows database-default nullable behavior. The model annotations/metadata use non-null semantics. This is evidence of a historical intent mismatch, not proof that either side is the owner of the defect.

## Required Closure Evidence

1. Confirm approved business semantics for NULL versus non-NULL.
2. Read-only inspect all historical rows and write paths beyond the current count baseline.
3. Decide whether the approved authority is database, model, or a later migration change.
4. Record the classification and risk approval per field.
5. Only after separate approval may a migration be designed; this report creates none.

