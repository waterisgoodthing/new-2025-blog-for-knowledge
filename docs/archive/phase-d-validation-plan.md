# Phase D Validation Plan

Date: 2026-07-15
Status: validation plan only; commands not executed.

## Before

Planned pre-execution checks:

| Check | Planned evidence | Status |
|---|---|---|
| Git status | `git status --short` with only expected implementation files dirty. | Planned |
| Migration current head | `alembic current` from `backend/` using the repository virtualenv and `PYTHONPATH=.`. | Planned; not executed |
| Database revision | Current `alembic_version` for the target database. | Planned; not executed |
| Backup readiness | Backup artifact, timestamp, location, and restore rehearsal result. | Planned |
| Scope match | Authorized files and operations match the approval record. | Planned |

## During

Planned execution-window checks:

| Check | Planned evidence | Status |
|---|---|---|
| Migration SQL | SQL review before execution; no unexpected DDL/DML. | Planned |
| Affected objects | Confirm only authorized objects are included. | Planned |
| Excluded scope | Confirm no `guest_messages`, `guest_message_bans`, data cleanup, destructive operation, unapproved nullable change, or index deletion. | Planned |
| Stop conditions | Operator stops if any stop condition is triggered. | Planned |

## After

Planned post-execution checks:

| Check | Planned evidence | Status |
|---|---|---|
| Application startup | Application starts without production `create_all` schema mutation. | Planned |
| Readiness validation | Readiness reports database connectivity and expected migration state. | Planned |
| Alembic state | Target database is at the expected revision. | Planned; not executed |
| Schema consistency | Database, Alembic metadata, and approved ORM metadata are consistent for the authorized scope. | Planned |
| Regression check | Relevant backend import/startup or targeted tests pass. | Planned |

## Current Status

```text
Validation Plan = PREPARED
Validation Execution = NOT STARTED
Execution Authorization = NOT APPROVED
```
