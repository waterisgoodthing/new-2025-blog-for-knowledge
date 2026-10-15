#!/usr/bin/env bash
set -u

RUN_ID="${PRA_RUN_ID:-pra06-single-shell-20260822}"
M30_COUNT="${PRA_M30_COUNT:-1}"
M30_MAX_ATTEMPTS="${PRA_M30_MAX_ATTEMPTS:-${M30_COUNT}}"
REPO="${PRA_REPO_ROOT:-$(cd "$(dirname "$0")/../../../../" && pwd)}"
ASSETS="$REPO/docs/workflows/production-render-readiness-acceptance/assets"
HEAD="$(git -C "$REPO" rev-parse HEAD)"
MAIN_STATUS_HASH="$(git -C "$REPO" status --short | shasum -a 256 | awk '{print $1}')"
FRONTEND_PORT="${PRA_FRONTEND_PORT:-3110}"
API_PORT="${PRA_API_PORT:-8110}"
PG_PORT="${PRA_PG_PORT:-55441}"
FRONTEND_BASE="http://api.localhost:${FRONTEND_PORT}"
API_BASE="http://api.localhost:${API_PORT}"
DB_NAME="pra06_single_shell"
DB_URL="postgresql+asyncpg://$(whoami)@127.0.0.1:${PG_PORT}/${DB_NAME}"
USERNAME="pra06-single-shell-admin"
ROOT=""
SNAPSHOT=""
API_PID=""
FRONTEND_PID=""
PG_DATA=""
JWT_SECRET_KEY="$(openssl rand -hex 32 2>/dev/null || printf 'runtime-only-secret')"
PROBE_EXIT="not_started"
CLEANED="false"

RUN_LOG="$ASSETS/${RUN_ID}.runner.log"
BUILD_LOG="$ASSETS/${RUN_ID}.build.log"
PREFLIGHT_LOG="$ASSETS/${RUN_ID}.preflight.log"
CLEANUP_LOG="$ASSETS/${RUN_ID}.cleanup.log"

mkdir -p "$ASSETS"
exec > >(tee -a "$RUN_LOG") 2>&1

stamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
record() { printf '%s=%s\n' "$1" "$2"; }

cleanup() {
  [ "$CLEANED" = "true" ] && return
  CLEANED="true"
  record cleanup_started "$(stamp)"
  if [ -n "$USERNAME" ] && [ -n "$SNAPSHOT" ] && [ -x "$SNAPSHOT/backend/.pra06-venv/bin/python" ]; then
    DATABASE_URL="$DB_URL" PYTHONPATH="$SNAPSHOT/backend" \
      "$SNAPSHOT/backend/.pra06-venv/bin/python" \
      "$ASSETS/pra06-cookie-diagnostic-20260822-seed.py" disable "$USERNAME" \
      >/dev/null 2>&1 || true
  fi
  for pid in "$FRONTEND_PID" "$API_PID"; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      for _ in 1 2 3 4 5; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
  done
  if [ -n "$PG_DATA" ] && [ -f "$PG_DATA/postmaster.pid" ]; then
    pg_ctl -D "$PG_DATA" stop -m fast >/dev/null 2>&1 || true
  fi
  if [ -n "$SNAPSHOT" ] && [ -d "$SNAPSHOT" ]; then
    git -C "$REPO" worktree remove --force "$SNAPSHOT" >/dev/null 2>&1 || true
  fi
  if [ -n "$ROOT" ] && [ -d "$ROOT" ]; then
    mkdir -p /Users/limengyang/.Trash
    mv "$ROOT" "/Users/limengyang/.Trash/$(basename "$ROOT")" 2>/dev/null || true
  fi
  record listeners_after_cleanup_3110 "$(lsof -nP -iTCP:3110 -sTCP:LISTEN 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
  record listeners_after_cleanup_8110 "$(lsof -nP -iTCP:8110 -sTCP:LISTEN 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
  record listeners_after_cleanup_55441 "$(lsof -nP -iTCP:55441 -sTCP:LISTEN 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
  record main_status_hash_after_cleanup "$(git -C "$REPO" status --short | shasum -a 256 | awk '{print $1}')"
  record cleanup_finished "$(stamp)"
}
trap cleanup EXIT INT TERM

record run_id "$RUN_ID"
record source_head "$HEAD"
record main_status_hash_before "$MAIN_STATUS_HASH"
record frontend_base "$FRONTEND_BASE"
record api_base "$API_BASE"
record postgres "127.0.0.1:${PG_PORT}/${DB_NAME}"
record auth_bypass false
record auth_bypass_allow false
record product_source_changed false
record m30_count "$M30_COUNT"
record m30_max_attempts "$M30_MAX_ATTEMPTS"

ROOT="$(mktemp -d "/private/tmp/${RUN_ID}-XXXXXX")"
SNAPSHOT="$ROOT/worktree"
PG_DATA="$ROOT/postgres/data"
mkdir -p "$ROOT/postgres"
git -C "$REPO" worktree add --detach "$SNAPSHOT" "$HEAD" > "$ASSETS/${RUN_ID}.snapshot.log" 2>&1 || exit 20
rsync -a --delete \
  --exclude '.git' --exclude '.git/' --exclude 'node_modules/' --exclude '.next/' \
  --exclude 'backend/.venv/' --exclude 'backend/.pra04-venv/' --exclude 'backend/.pra06-venv/' \
  --exclude '.cluster/' --exclude '.kilo/' --exclude 'test-results/' \
  --exclude '.env' --exclude '.env.*' --exclude 'backend/.env' \
  "$REPO/" "$SNAPSHOT/" > "$ASSETS/${RUN_ID}.snapshot-rsync.log" 2>&1 || exit 21

NODE_PREFIX="/opt/homebrew/opt/node@24/bin"
PATH="$NODE_PREFIX:$PATH"
export PATH
npm ci --prefix "$SNAPSHOT" --no-audit --no-fund > "$ASSETS/${RUN_ID}.npm-ci.log" 2>&1 || exit 22
[ -x "$SNAPSHOT/node_modules/.bin/next" ] || exit 23
if command -v python3.12 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3.12)"; else PYTHON_BIN="/opt/homebrew/bin/python3.12"; fi
"$PYTHON_BIN" -m venv "$SNAPSHOT/backend/.pra06-venv" > "$ASSETS/${RUN_ID}.venv.log" 2>&1 || exit 24
"$SNAPSHOT/backend/.pra06-venv/bin/pip" install -r "$SNAPSHOT/backend/requirements.txt" > "$ASSETS/${RUN_ID}.pip-install.log" 2>&1 || exit 25

NEXT_PUBLIC_API_URL="$API_BASE" NEXT_PUBLIC_SITE_URL="$FRONTEND_BASE" \
  npm --prefix "$SNAPSHOT" run build > "$BUILD_LOG" 2>&1 || exit 26

initdb -D "$PG_DATA" -U "$(whoami)" -A trust --no-locale --encoding=UTF8 > "$ASSETS/${RUN_ID}.postgres-init.log" 2>&1 || exit 27
pg_ctl -D "$PG_DATA" -l "$ROOT/postgres/postgres.log" -o "-p ${PG_PORT} -h 127.0.0.1" start > "$ASSETS/${RUN_ID}.postgres-start.log" 2>&1 || exit 28
createdb -h 127.0.0.1 -p "$PG_PORT" -U "$(whoami)" "$DB_NAME" || exit 29
export DATABASE_URL="$DB_URL"
export PYTHONPATH="$SNAPSHOT/backend"
export ENV=production
export ENABLE_REGISTRATION=false
export ALLOWED_ORIGINS="$FRONTEND_BASE"
export AUTH_BYPASS=false
export AUTH_BYPASS_ALLOW=false
export JWT_SECRET_KEY
export WEBAUTHN_ORIGIN="$FRONTEND_BASE"
export WEBAUTHN_RP_ID=api.localhost
(
  cd "$SNAPSHOT/backend" || exit 30
  "$SNAPSHOT/backend/.pra06-venv/bin/alembic" -c alembic.ini upgrade head
) > "$ASSETS/${RUN_ID}.migration.log" 2>&1 || exit 30

(
  cd "$SNAPSHOT/backend" || exit 31
  exec env DATABASE_URL="$DB_URL" PYTHONPATH="$SNAPSHOT/backend" ENV=production ENABLE_REGISTRATION=false \
    ALLOWED_ORIGINS="$FRONTEND_BASE" AUTH_BYPASS=false AUTH_BYPASS_ALLOW=false \
    JWT_SECRET_KEY="$JWT_SECRET_KEY" WEBAUTHN_ORIGIN="$FRONTEND_BASE" WEBAUTHN_RP_ID=api.localhost \
    "$SNAPSHOT/backend/.pra06-venv/bin/uvicorn" main:app --host 127.0.0.1 --port "$API_PORT"
) > "$ASSETS/${RUN_ID}.api.log" 2>&1 &
API_PID=$!
(
  cd "$SNAPSHOT" || exit 32
  exec env NEXT_PUBLIC_API_URL="$API_BASE" NODE_ENV=production npm run start -- -H 127.0.0.1 -p "$FRONTEND_PORT"
) > "$ASSETS/${RUN_ID}.frontend.log" 2>&1 &
FRONTEND_PID=$!

for _ in $(seq 1 60); do
  api_ok=false
  frontend_ok=false
  curl -fsS --max-time 2 "http://127.0.0.1:${API_PORT}/api/health" >/dev/null 2>&1 && api_ok=true
  curl -fsS --max-time 2 --resolve "api.localhost:${FRONTEND_PORT}:127.0.0.1" "$FRONTEND_BASE/manage" >/dev/null 2>&1 && frontend_ok=true
  if [ "$api_ok" = true ] && [ "$frontend_ok" = true ]; then break; fi
  sleep 1
done
curl -fsS "http://127.0.0.1:${API_PORT}/api/health" > "$ASSETS/${RUN_ID}.api-health.json" || exit 33
curl -fsS --resolve "api.localhost:${API_PORT}:127.0.0.1" "$API_BASE/api/health" > "$ASSETS/${RUN_ID}.api-host-health.json" || exit 34
for _ in 1 2 3 4 5; do
  kill -0 "$API_PID" 2>/dev/null || exit 35
  kill -0 "$FRONTEND_PID" 2>/dev/null || exit 36
  sleep 1
done
{
  record preflight_health 200
  record api_pid "$API_PID"
  record frontend_pid "$FRONTEND_PID"
  record api_process_alive true
  record frontend_process_alive true
  printf '%s\n' 'cors_preflight:'
  curl -sS --resolve "api.localhost:${API_PORT}:127.0.0.1" -D - -o /dev/null -X OPTIONS "$API_BASE/api/auth/login" \
    -H "Origin: $FRONTEND_BASE" -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: content-type'
} > "$PREFLIGHT_LOG" 2>&1 || exit 37

set +e
(
  cd "$SNAPSHOT" || exit 38
  env DATABASE_URL="$DB_URL" PYTHONPATH="$SNAPSHOT/backend" \
    PRA_ASSET_DIR="$ASSETS" PRA_RUN_ID="$RUN_ID" PRA_M30_BATCH_ID="$RUN_ID" \
    PRA_M30_COUNT="$M30_COUNT" PRA_M30_MAX_ATTEMPTS="$M30_MAX_ATTEMPTS" \
    PRA_FRONTEND_BASE="$FRONTEND_BASE" \
    PRA_API_BASE="$API_BASE" PRA_API_BIND="http://127.0.0.1:${API_PORT}" \
    PRA_ISOLATED_WORKTREE="$SNAPSHOT" PRA_ISOLATED_PYTHON="$SNAPSHOT/backend/.pra06-venv/bin/python" \
    PRA_SEED_FILE="$ASSETS/pra06-cookie-diagnostic-20260822-seed.py" \
    PRA06_TEMP_USERNAME="$USERNAME" \
    node "$SNAPSHOT/docs/workflows/production-render-readiness-acceptance/assets/pra06-m30-batch-controller-20260822.mjs"
)
PROBE_EXIT=$?
set -e
record probe_exit "$PROBE_EXIT"
exit 0
