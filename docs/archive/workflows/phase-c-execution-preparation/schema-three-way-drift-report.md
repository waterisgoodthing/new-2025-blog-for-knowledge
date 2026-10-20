# Schema Three-Way Drift Report

日期：2026-07-14  
范围：Database Schema vs SQLAlchemy Model Metadata vs Alembic Migration History。  
结论纪律：不直接把任何差异判定为 database error、model error 或 migration missing；每项保留分类与 UNKNOWN 边界。

## Three-Way Baseline

| Layer | Observed evidence |
|---|---|
| Database Schema | 当前 PostgreSQL `public` schema：38 tables（含 `alembic_version`）；focused metadata query 读取 columns、defaults、indexes、PK/FK for `folders`/`notes`；全库 constraint counts：PK 38、FK 35、CHECK 41、UNIQUE 17；indexes 105 |
| SQLAlchemy Model Metadata | runtime `Base.metadata`：37 model tables；focused model inspection reads type, nullable, Python default, server default, indexes for `folders`/`notes` |
| Alembic Migration History | `018 (head)`，单链；revision `005` creates `folders`, `notes.folder_id`, `notes.sort_order`, `idx_notes_folder_id`; `007` changes folder parent delete behavior to `SET NULL`; static inventory finds 35 `create_table` tables |

## Column Comparison

| Object | Database | SQLAlchemy metadata | Migration history | Required classification | Status |
|---|---|---|---|---|---|
| `folders.sort_order` | `integer`, nullable, default `0` | `Integer`, `nullable=False`, Python default `0`，无 server default | 005 creates integer, omitted nullable (database default nullable), server default `0` | `unknown`: possible model intent drift, migration omission, or database drift | BLOCKED |
| `folders.created_at` | `timestamp without time zone`, nullable, default `now()` | `DateTime`, `nullable=False`, server default `now()` | 005 creates DateTime, omitted nullable, server default `now()` | `unknown`: nullable semantics differ; no NULL-row impact evidence in current report | BLOCKED |
| `folders.updated_at` | `timestamp without time zone`, nullable, default `now()` | `DateTime`, `nullable=False`, server default `now()` | 005 creates DateTime, omitted nullable, server default `now()` | `unknown`: nullable semantics differ; update behavior must be reconciled | BLOCKED |
| `notes.sort_order` | `integer`, nullable, default `0` | `Integer`, `nullable=False`, Python default `0`，无 server default | 005 adds integer, omitted nullable, server default `0` | `unknown`: possible model intent drift, migration omission, or database drift | BLOCKED |

### Column interpretation boundary

For the four columns, data types and observed defaults are broadly compatible, while nullable semantics differ. This is not sufficient to decide the owner of the discrepancy. Required follow-up is a read-only NULL-row count, exact model/migration intent review, and approved policy for existing NULL values; no NOT NULL change is authorized by this report.

## Index Comparison

| Index | Database | SQLAlchemy metadata | Migration history | Required classification | Status |
|---|---|---|---|---|---|
| `idx_notes_folder_id` | present: btree(`folder_id`), non-unique | absent from `Note.__table_args__` | created by 005; downgrade drops it | `unknown`: possible model metadata omission or intentionally retained historical index; current database is consistent with recorded 005 creation | BLOCKED |

The index difference must not be resolved by deleting/recreating the index or by generating a migration in Phase C+1.

## Constraint Comparison

Focused constraints for the affected tables are present in database metadata:

- `folders_pkey` and `notes_pkey` are primary keys;
- `folders_parent_id_fkey` references `folders.id` with `ON DELETE SET NULL`;
- `notes_folder_id_fkey` references `folders.id` with `ON DELETE SET NULL`.

The model declares the same FK targets and `SET NULL`; migration `007` records the parent delete behavior change, and the database currently reflects `SET NULL`. No focused PK/FK discrepancy was observed. CHECK constraints do not apply to these four drift fields. This does not replace a full all-table constraint diff before Gate closure.

## Classification Rules and Closure Evidence

| Classification | Meaning | Evidence needed before using it |
|---|---|---|
| `database drift` | database differs from approved model/migration intent | exact DDL, provenance, NULL/data impact, approved target |
| `model drift` | model metadata differs from approved database/migration intent | model ownership decision and test impact |
| `migration omission` | approved model/schema change has no history operation | design decision and later approved migration plan |
| `metadata registration issue` | object is not visible because import/registration is incomplete | isolated import experiment and explicit coverage inventory |
| `unknown` | evidence cannot safely distinguish the above | remains blocking; no auto-remediation |

Current unresolved items: all five reported drift items remain `unknown`/blocking. Metadata coverage additionally has two model tables with no migration create provenance, also `unknown` with migration omission/create_all candidate risk.

