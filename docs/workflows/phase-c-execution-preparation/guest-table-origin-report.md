# Guest Table Origin Report

日期：2026-07-14  
对象：`guest_messages`、`guest_message_bans`。  
结论纪律：repository intent 不等于 current database provenance；无记录处标记 `UNKNOWN`。

## Repository Evidence

| Area | Evidence | Finding |
|---|---|---|
| Model definition | `backend/app/models/guest_message.py:11-49` | `GuestMessage` and `GuestMessageBan` are SQLAlchemy models in `Base.metadata` |
| Model registry | `backend/app/models/__init__.py:9,38-39` | Both models are exported and imported during package initialization |
| Router | `backend/app/routers/guest_messages.py` | Public create/list and admin moderation/ban queries use both models directly |
| Schema | `backend/app/schemas/guest_message.py` | Request/response contracts exist |
| Application registration | `backend/main.py:13,96` | `guest_messages.router` is imported and included |
| Alembic migration | `backend/alembic/versions/*` | No `create_table('guest_messages')` or `create_table('guest_message_bans')` record found |
| Scripts/deployment | repository-wide `rg` over `backend/`, `alembic/`, `scripts/`, `deployment/`, `docs/` | No initialization script or deployment DDL record found; docs contain design/validation notes only |
| Existing docs | `docs/workflows/public-site-closure-upgrade/validation.md:88` | Explicitly records migration not yet generated and dev auto-creation via `Base.metadata.create_all` |

## Question 1: Why Do These Tables Exist?

Allowed classifications:

| Classification | Evidence status |
|---|---|
| `migration-created` | NOT SUPPORTED: no migration create record found |
| `create_all-created` | PLAUSIBLE repository/dev path: existing docs explicitly describe dev auto-creation, but current DB audit log/provenance is absent |
| `manual-created` | UNKNOWN: no manual DDL record found |
| `external-provisioning` | UNKNOWN: no external provisioning record found |
| `unknown` | CURRENT CLASSIFICATION |

The defensible conclusion is `unknown`, with `create_all-created` as the strongest documented candidate for a development database. It is not safe to transfer that candidate into a production/current-database fact.

## Question 2: Are These Official Schema?

| Classification | Evidence status |
|---|---|
| `official-schema` | NOT CLOSED: models, router, schemas and docs indicate intended application feature, but versioned migration authority is absent |
| `legacy-schema` | UNKNOWN: no deprecation/removal record found |
| `orphan-schema` | NOT SUPPORTED: active router/model references exist |
| `unknown` | CURRENT FORMAL SCHEMA CLASSIFICATION |

They are active application-domain objects, but their status as formally versioned official schema is `UNKNOWN`. They must not be included in a migration scope until provenance and authority are explicitly approved.

## Database Shape Evidence

Current database SELECT inspection found both tables and their model-aligned columns/indexes. This proves existence only; it does not prove which provisioning path created them.

## Closure Requirement

To close provenance, obtain an approved source snapshot/provisioning log or isolate the database creation history. Until that exists, do not generate a migration to retroactively assert provenance, and do not delete or alter either table.

