# Phase D-3 Alembic Validation

Date: 2026-07-15
Mode: read-only Alembic validation.

## Commands

```bash
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic history --verbose
PYTHONPATH=. .venv/bin/alembic heads --verbose
```

## Revision

Expected revision:

```text
018
```

Observed current revision:

```text
018 (head)
```

## Revision Graph

`alembic history --verbose` reported a chain ending at:

```text
Rev: 018 (head)
Parent: 017
Path: backend/alembic/versions/018_add_ai_runs.py
```

The inspected graph includes historical non-numeric revisions in the chain:

```text
002 -> 0ec85724afb9 -> 1119bee5a419 -> 003 -> 004 -> ... -> 018
```

## Multiple Heads

`alembic heads --verbose` reported:

```text
Rev: 018 (head)
Parent: 017
```

No multiple-head condition was reported.

## Broken Chain

No broken chain was reported by `history` or `heads`.

## Alembic Check

Command:

```bash
PYTHONPATH=. .venv/bin/alembic check
```

Result:

```text
FAILED
```

Detected proposed operations include:

- removal of `guest_message_bans`;
- removal of `guest_messages`;
- removal of guest-message indexes;
- nullable changes for `folders.sort_order`;
- nullable changes for `folders.created_at`;
- nullable changes for `folders.updated_at`;
- nullable changes for `notes.sort_order`.

These are explicitly outside the approved execution scope.

## Validation Result

```text
Alembic current = PASS
Alembic history = PASS
Alembic heads = PASS
Alembic check = FAIL
```

No Alembic upgrade or downgrade was executed.
