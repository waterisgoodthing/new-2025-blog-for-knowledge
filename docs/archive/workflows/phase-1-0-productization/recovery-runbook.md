# v1.0 Recovery Runbook

## Purpose

Restore the revision `020` PostgreSQL database and private attachment storage into an isolated environment before any recovery is attempted against the normal runtime. This runbook never uses the source database as a restore target.

## Verified Backup Set

| Artifact | SHA-256 |
|---|---|
| `/Users/limengyang/.codex/backups/2025-blog-public/phase-1-0b/blog_db-phase-1-0b-rev020-20260719T112321+0800.dump` | `1f7c9ba0965365fca13f30932884b69d8cda251a76400904c38dc34eb33c8b79` |
| `/Users/limengyang/.codex/backups/2025-blog-public/phase-1-0b/attachments-phase-1-0b-20260719T112420+0800.manifest.tsv` | `906693fd5694339d44a96935e040c34962aea6f562302f9e54c5312378f32715` |
| `/Users/limengyang/.codex/backups/2025-blog-public/phase-1-0b/attachments-phase-1-0b-20260719T112420+0800.tar.gz` | `beb4809c54f2c02219f84c686bdb60ec3d6f0b4cd8e96f080ef9fdbb662b76be` |

The set was restore-proven on 2026-07-19. A hash match proves artifact identity; the isolated restore remains the proof of usability.

## 1. Preflight

1. Confirm `pg_dump`, `pg_restore`, `initdb`, `pg_ctl`, `createdb`, `psql`, `tar` and `shasum` are available.
2. Record the normal database revision and read-only counts before recovery work.
3. Confirm the selected PostgreSQL and application ports are unused.
4. Never print `DATABASE_URL`, session cookies, tokens or `.env` contents into the run log.

Verify artifacts before extraction:

```bash
shasum -a 256 "$DUMP" "$ATTACHMENT_MANIFEST" "$ATTACHMENT_ARCHIVE"
pg_restore --list "$DUMP" >/dev/null
tar -tzf "$ATTACHMENT_ARCHIVE" >/dev/null
```

Stop immediately if any hash differs from the verified table.

## 2. Isolated PostgreSQL Restore

Create a short temporary root under `/private/tmp`, initialize PostgreSQL with local trust authentication, bind only to `127.0.0.1` on an unused port, and create a new empty database.

```bash
TMP_ROOT=$(mktemp -d /private/tmp/blog-restore.XXXXXX)
PGDATA="$TMP_ROOT/pgdata"
RESTORE_ROOT="$TMP_ROOT/uploads"

initdb -D "$PGDATA" -A trust --no-locale
pg_ctl -D "$PGDATA" -o "-h 127.0.0.1 -p $PG_PORT -k $TMP_ROOT" -w start
createdb -h 127.0.0.1 -p "$PG_PORT" blog_restore
pg_restore --exit-on-error --no-owner --no-privileges \
  -h 127.0.0.1 -p "$PG_PORT" -d blog_restore "$DUMP"
```

Do not substitute the normal database name or port.

## 3. Attachment Restore

```bash
mkdir -p "$RESTORE_ROOT"
tar -C "$RESTORE_ROOT" -xzf "$ATTACHMENT_ARCHIVE"
```

For every non-deleted `attachments` row, verify that `RESTORE_ROOT/storage_key` exists and that its byte count and SHA-256 equal `size_bytes` and `checksum_sha256`. A database-only restore is not sufficient.

## 4. Application Verification

Point only the temporary process at the isolated resources:

```bash
export DATABASE_URL="postgresql+asyncpg://127.0.0.1:$PG_PORT/blog_restore"
export UPLOAD_ROOT="$RESTORE_ROOT"
export KEEP_ALIVE_ENABLED=false

cd backend
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/uvicorn main:app --host 127.0.0.1 --port "$APP_PORT"
```

Acceptance:

- Alembic reports `020 (head)`.
- FastAPI completes its startup revision check.
- `GET /api/health` returns 200 with `{"status":"ok"}`.
- public `GET /api/notes` returns 200.
- restored core counts equal the backup snapshot.
- all active attachment checksums match.
- the normal source revision and counts remain identical before and after.

`PYTHONPATH=.` is required for the repository's Alembic import path.

## 5. Cleanup

1. Stop the temporary application process.
2. Stop the isolated cluster with `pg_ctl -D "$PGDATA" -m fast stop`.
3. Confirm neither temporary port is listening and no `postmaster.pid` remains active.
4. Delete only the exact temporary root created in step 2.
5. Retain backup artifacts and this validation record.

## 6. Incident Rules

- Hash mismatch: quarantine the artifact; do not restore it.
- `pg_restore` failure: stop and preserve its log; do not retry against the source DB.
- Revision other than `020`: do not start the application and do not run `alembic upgrade` automatically.
- Attachment mismatch: treat recovery as failed even when PostgreSQL is healthy.
- Diagnostics `database` or `storage` not `ok`: keep the normal runtime out of service until the cause is understood.
- Never enable `AUTH_BYPASS` to complete recovery acceptance.

## Current Release Constraint

`alembic current`, the verified isolated restore, and the current `alembic check` all pass at revision `020`. Schema Authority Gate selected SA-A and aligned lifecycle metadata with the existing physical knowledge-point contract without changing the revision or recovery boundary. The verified backup remains applicable; RC must still revalidate runtime, permissions and final acceptance evidence.
