#!/usr/bin/env bash
set -euo pipefail

PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MUSIC_REL="public/mymusic"
MUSIC_DIR="${REPO_ROOT}/${MUSIC_REL}"
PUBLIC_SITE="https://blog.limengyang.me"
PUBLIC_API="https://public-api.limengyang.me"
ROUTE="blog.limengyang.me/*"
ASSET_LIMIT_BYTES=$((25 * 1024 * 1024))
SELECTION_FILE_NAME="selection.json"
LAUNCH_AGENT_LABEL="com.blog.mymusic.deploy"
LAUNCH_AGENT_PLIST="${HOME}/Library/LaunchAgents/${LAUNCH_AGENT_LABEL}.plist"
LAUNCH_AGENT_LOG="/tmp/blog-mymusic-deploy.log"
DEPLOY_LOCK_DIR="${TMPDIR:-/tmp}/blog-mymusic-deploy.lock"
INTERVAL_SECONDS=5
DEBOUNCE_SECONDS=10
MODE="watch"
RUN_DEPLOY=1
VERIFY_BUILD_ONLY=0
CURRENT_TEMP_ROOT=""
CURRENT_WORKTREE=""

SUPPORTED_AUDIO_EXTENSIONS=" mp3 m4a aac ogg opus webm wav "

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: scripts/watch-mymusic-deploy.sh [options]

Options:
  --watch             Watch public/mymusic continuously. Default.
  --once              Run one deployment cycle now.
  --check             Run one safe check cycle without deploying.
  --verify-build      Run tsc in the clean worktree without building or deploying.
  --install-launch-agent
                      Install and start the macOS LaunchAgent watcher.
  --uninstall-launch-agent
                      Stop and remove the macOS LaunchAgent watcher.
  --status-launch-agent
                      Show macOS LaunchAgent status.
  --no-deploy         Prepare and validate, but do not deploy.
  --interval SECONDS  Watch polling interval. Default: 5.
  --debounce SECONDS  Delay after detected changes. Default: 10.
  -h, --help          Show this help.

The deploy cycle always builds from a temporary clean git worktree at HEAD,
then overlays only public/mymusic from the active workspace.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --watch)
      MODE="watch"
      ;;
    --once)
      MODE="once"
      ;;
    --check)
      MODE="check"
      RUN_DEPLOY=0
      ;;
    --verify-build)
      MODE="verify-build"
      RUN_DEPLOY=0
      VERIFY_BUILD_ONLY=1
      ;;
    --install-launch-agent)
      MODE="install-launch-agent"
      RUN_DEPLOY=0
      ;;
    --uninstall-launch-agent)
      MODE="uninstall-launch-agent"
      RUN_DEPLOY=0
      ;;
    --status-launch-agent)
      MODE="status-launch-agent"
      RUN_DEPLOY=0
      ;;
    --no-deploy)
      RUN_DEPLOY=0
      ;;
    --interval)
      shift
      INTERVAL_SECONDS="${1:-}"
      ;;
    --debounce)
      shift
      DEBOUNCE_SECONDS="${1:-}"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown option: $1"
      ;;
  esac
  shift
done

case "${INTERVAL_SECONDS}" in
  ''|*[!0-9]*) fail "--interval must be a positive integer" ;;
esac
case "${DEBOUNCE_SECONDS}" in
  ''|*[!0-9]*) fail "--debounce must be a positive integer" ;;
esac

require_repo() {
  [[ -d "${REPO_ROOT}/.git" ]] || fail "Not in expected repository root: ${REPO_ROOT}"
  [[ -f "${REPO_ROOT}/package.json" ]] || fail "package.json not found in ${REPO_ROOT}"
  [[ -f "${REPO_ROOT}/wrangler.toml" ]] || fail "wrangler.toml not found in ${REPO_ROOT}"
  [[ -d "${MUSIC_DIR}" ]] || fail "Music directory not found: ${MUSIC_DIR}"
}

is_supported_audio_file() {
  local path="$1"
  local name ext
  name="$(basename "$path")"
  ext="${name##*.}"
  ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  [[ "${name}" == *.* && "${SUPPORTED_AUDIO_EXTENSIONS}" == *" ${ext} "* ]]
}

selected_audio_file() {
  local configured
  configured="$(configured_selected_file || true)"
  if [[ -n "${configured}" ]]; then
    local configured_path="${MUSIC_DIR}/${configured}"
    if [[ -f "${configured_path}" ]] && is_supported_audio_file "${configured_path}" && is_deployable_asset "${configured_path}"; then
      basename "${configured_path}"
      return 0
    fi
  fi

  find "${MUSIC_DIR}" -maxdepth 1 -type f | sort | while IFS= read -r path; do
    if is_supported_audio_file "$path" && is_deployable_asset "$path"; then
      basename "$path"
      return 0
    fi
  done
}

configured_selected_file() {
  local selection_path="${MUSIC_DIR}/${SELECTION_FILE_NAME}"
  [[ -f "${selection_path}" ]] || return 0
  node -e '
    const fs = require("fs");
    try {
      const value = JSON.parse(fs.readFileSync(process.argv[1], "utf8")).selected_file;
      if (typeof value === "string" && value && !value.includes("/") && !value.includes("\\")) {
        console.log(value);
      }
    } catch {}
  ' "${selection_path}"
}

is_deployable_asset() {
  local path="$1"
  local size
  size="$(stat -f '%z' "$path")"
  [[ "${size}" -le "${ASSET_LIMIT_BYTES}" ]]
}

audio_count() {
  local count=0
  while IFS= read -r path; do
    if is_supported_audio_file "$path"; then
      count=$((count + 1))
    fi
  done < <(find "${MUSIC_DIR}" -maxdepth 1 -type f | sort)
  printf '%s\n' "$count"
}

urlencode() {
  node -e 'console.log(encodeURIComponent(process.argv[1]))' "$1"
}

music_fingerprint() {
  if [[ ! -d "${MUSIC_DIR}" ]]; then
    printf 'missing\n'
    return 0
  fi

  find "${MUSIC_DIR}" -maxdepth 1 -type f | sort | while IFS= read -r path; do
    local rel size mtime hash
    rel="${path#${MUSIC_DIR}/}"
    size="$(stat -f '%z' "$path")"
    mtime="$(stat -f '%m' "$path")"
    hash="$(shasum -a 256 "$path" | awk '{print $1}')"
    printf '%s\t%s\t%s\t%s\n' "$rel" "$size" "$mtime" "$hash"
  done | shasum -a 256 | awk '{print $1}'
}

normalize_music_permissions() {
  log "Normalizing readable permissions under ${MUSIC_REL}"
  find "${MUSIC_DIR}" -type d -exec chmod 755 {} +
  find "${MUSIC_DIR}" -type f -exec chmod 644 {} +
}

copy_music_overlay() {
  local target_root="$1"
  mkdir -p "${target_root}/${MUSIC_REL}"
  rm -rf "${target_root}/${MUSIC_REL:?}/"*

  local selected
  selected="$(selected_audio_file || true)"

  if [[ -f "${MUSIC_DIR}/.gitkeep" ]]; then
    cp "${MUSIC_DIR}/.gitkeep" "${target_root}/${MUSIC_REL}/.gitkeep"
  fi
  if [[ -f "${MUSIC_DIR}/${SELECTION_FILE_NAME}" ]]; then
    cp "${MUSIC_DIR}/${SELECTION_FILE_NAME}" "${target_root}/${MUSIC_REL}/${SELECTION_FILE_NAME}"
  fi

  find "${MUSIC_DIR}" -maxdepth 1 -type f | sort | while IFS= read -r path; do
    local name
    name="$(basename "$path")"
    if ! is_supported_audio_file "$path"; then
      continue
    fi
    if ! is_deployable_asset "$path"; then
      log "Skipping oversized audio asset: ${name}"
      continue
    fi
    cp "$path" "${target_root}/${MUSIC_REL}/${name}"
  done

  if [[ -n "${selected}" && ! -f "${target_root}/${MUSIC_REL}/${selected}" ]]; then
    fail "Selected audio was not copied to deploy worktree: ${selected}"
  fi
}

validate_selected_asset() {
  local configured selected_path size
  configured="$(configured_selected_file || true)"
  [[ -n "${configured}" ]] || return 0

  selected_path="${MUSIC_DIR}/${configured}"
  if [[ ! -f "${selected_path}" ]]; then
    fail "Selected music file does not exist: ${configured}"
  fi
  if ! is_supported_audio_file "${selected_path}"; then
    fail "Selected music file is not a supported browser-playable audio file: ${configured}"
  fi
  size="$(stat -f '%z' "${selected_path}")"
  if [[ "${size}" -gt "${ASSET_LIMIT_BYTES}" ]]; then
    fail "Selected music file exceeds Cloudflare Workers 25 MiB asset limit: ${configured} ($(human_bytes "${size}")). Compress it or select a smaller file."
  fi
}

human_bytes() {
  node -e '
    const bytes = Number(process.argv[1]);
    const units = ["B", "KiB", "MiB", "GiB"];
    let value = bytes;
    let index = 0;
    while (value >= 1024 && index < units.length - 1) {
      value /= 1024;
      index++;
    }
    console.log(`${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`);
  ' "$1"
}

install_launch_agent() {
  require_repo
  mkdir -p "${HOME}/Library/LaunchAgents"
  cat > "${LAUNCH_AGENT_PLIST}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LAUNCH_AGENT_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>source ~/.zshrc >/dev/null 2>&amp;1 || true; cd ${REPO_ROOT}; exec ${REPO_ROOT}/scripts/watch-mymusic-deploy.sh --watch</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${REPO_ROOT}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LAUNCH_AGENT_LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LAUNCH_AGENT_LOG}</string>
</dict>
</plist>
EOF
  chmod 644 "${LAUNCH_AGENT_PLIST}"
  launchctl bootout "gui/$(id -u)" "${LAUNCH_AGENT_PLIST}" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "${LAUNCH_AGENT_PLIST}"
  launchctl enable "gui/$(id -u)/${LAUNCH_AGENT_LABEL}" >/dev/null 2>&1 || true
  log "Installed LaunchAgent ${LAUNCH_AGENT_LABEL}"
  log "Logs: ${LAUNCH_AGENT_LOG}"
}

uninstall_launch_agent() {
  launchctl bootout "gui/$(id -u)" "${LAUNCH_AGENT_PLIST}" >/dev/null 2>&1 || true
  rm -f "${LAUNCH_AGENT_PLIST}"
  log "Removed LaunchAgent ${LAUNCH_AGENT_LABEL}"
}

status_launch_agent() {
  if [[ -f "${LAUNCH_AGENT_PLIST}" ]]; then
    log "LaunchAgent plist exists: ${LAUNCH_AGENT_PLIST}"
  else
    log "LaunchAgent plist is not installed: ${LAUNCH_AGENT_PLIST}"
  fi
  launchctl print "gui/$(id -u)/${LAUNCH_AGENT_LABEL}" 2>/dev/null || true
}

prepare_node_dependencies() {
  local target_root="$1"

  if [[ ! -f "${target_root}/package-lock.json" ]]; then
    fail "Temporary worktree missing package-lock.json; cannot install deterministic deploy dependencies."
  fi

  log "Installing deploy dependencies inside temporary worktree"
  (
    cd "${target_root}"
    npm ci --prefer-offline --no-audit --no-fund
  )
}

prepare_next_type_declarations() {
  local target_root="$1"

  if [[ ! -f "${target_root}/next-env.d.ts" ]]; then
    log "Creating temporary Next.js type declarations"
    cat > "${target_root}/next-env.d.ts" <<'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: Temporary deploy-worktree file generated by scripts/watch-mymusic-deploy.sh.
EOF
  fi
}

copy_deploy_env_files() {
  local target_root="$1"
  local copied=0
  local env_file

  for env_file in .env.production .env.production.local; do
    if [[ -f "${REPO_ROOT}/${env_file}" ]]; then
      cp "${REPO_ROOT}/${env_file}" "${target_root}/${env_file}"
      copied=1
    fi
  done

  if [[ "${copied}" -eq 1 ]]; then
    log "Copied production env file(s) into temporary worktree"
  else
    log "No production env file found in active workspace"
  fi
}

verify_public_outputs() {
  local selected="$1"

  if [[ -n "${selected}" ]]; then
    local encoded static_url status
    encoded="$(urlencode "${selected}")"
    static_url="${PUBLIC_SITE}/mymusic/${encoded}"
    log "Verifying public static audio: ${static_url}"
    status="$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 30 -I "${static_url}" || true)"
    if [[ "${status}" == "200" ]]; then
      log "Static audio verification passed: HTTP 200"
    else
      log "Static audio verification failed: HTTP ${status}"
      return 1
    fi
  else
    log "No supported audio file found; skipping static audio URL verification"
  fi

  log "Verifying public music API: ${PUBLIC_API}/api/music/manage/daily-song/public"
  local api_body
  api_body="$(curl -sS --max-time 30 "${PUBLIC_API}/api/music/manage/daily-song/public" || true)"
  if [[ -n "${selected}" && "${api_body}" == "null" ]]; then
    log "Public API still returns null; backend runtime may not see the deployed music file yet"
    return 1
  fi
  log "Public API response: ${api_body}"
}

cleanup_worktree() {
  local temp_root="$1"
  local worktree="$2"
  if [[ -n "${worktree}" && -d "${worktree}" ]]; then
    git -C "${REPO_ROOT}" worktree remove --force "${worktree}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${temp_root}" && -d "${temp_root}" ]]; then
    rm -rf "${temp_root}"
  fi
}

cleanup_current_worktree() {
  cleanup_worktree "${CURRENT_TEMP_ROOT}" "${CURRENT_WORKTREE}"
  CURRENT_TEMP_ROOT=""
  CURRENT_WORKTREE=""
}

release_deploy_lock() {
  rmdir "${DEPLOY_LOCK_DIR}" >/dev/null 2>&1 || true
}

trap 'release_deploy_lock; cleanup_current_worktree' EXIT INT TERM

run_cycle() {
  require_repo

  if ! mkdir "${DEPLOY_LOCK_DIR}" 2>/dev/null; then
    log "Another music deploy cycle is already running; skipping this trigger"
    return 0
  fi

  local selected count
  selected="$(selected_audio_file || true)"
  count="$(audio_count)"

  log "Detected supported audio files: ${count}"
  if [[ -n "${selected}" ]]; then
    log "Selected audio file: ${selected}"
  else
    log "No supported audio file selected"
  fi

  normalize_music_permissions
  validate_selected_asset

  cleanup_current_worktree
  CURRENT_TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/mymusic-deploy.XXXXXX")"
  CURRENT_WORKTREE="${CURRENT_TEMP_ROOT}/worktree"

  log "Creating clean temporary worktree from HEAD: ${CURRENT_WORKTREE}"
  git -C "${REPO_ROOT}" worktree add --detach --quiet "${CURRENT_WORKTREE}" HEAD

  [[ -f "${CURRENT_WORKTREE}/package.json" ]] || fail "Temporary worktree missing package.json"
  [[ -f "${CURRENT_WORKTREE}/wrangler.toml" ]] || fail "Temporary worktree missing wrangler.toml"

  log "Overlaying ${MUSIC_REL} into temporary worktree"
  copy_music_overlay "${CURRENT_WORKTREE}"
  prepare_node_dependencies "${CURRENT_WORKTREE}"
  prepare_next_type_declarations "${CURRENT_WORKTREE}"
  copy_deploy_env_files "${CURRENT_WORKTREE}"

  if [[ "${RUN_DEPLOY}" -eq 0 ]]; then
    if [[ "${VERIFY_BUILD_ONLY}" -eq 1 ]]; then
      log "Verify-build mode: running type-check from temporary worktree"
      (
        cd "${CURRENT_WORKTREE}"
        npx tsc --noEmit
      )
      cleanup_current_worktree
      release_deploy_lock
      return 0
    fi
    log "No-deploy mode: skipping type-check, build, deploy, and public verification"
    log "Prepared temporary deploy root: ${CURRENT_WORKTREE}"
    cleanup_current_worktree
    release_deploy_lock
    return 0
  fi

  log "Running deploy sequence from temporary worktree"
  (
    cd "${CURRENT_WORKTREE}"
    npx tsc --noEmit
    npm run build:cf
    npx wrangler deploy --route "${ROUTE}"
  )

  verify_public_outputs "${selected}"
  cleanup_current_worktree
  release_deploy_lock
}

watch_loop() {
  require_repo

  local last current
  last="$(music_fingerprint)"
  log "Watching ${MUSIC_REL}; initial fingerprint ${last}"
  log "Press Ctrl-C to stop"

  while true; do
    sleep "${INTERVAL_SECONDS}"
    current="$(music_fingerprint)"
    if [[ "${current}" != "${last}" ]]; then
      log "Change detected in ${MUSIC_REL}; waiting ${DEBOUNCE_SECONDS}s before deploy"
      sleep "${DEBOUNCE_SECONDS}"
      current="$(music_fingerprint)"
      run_cycle
      last="${current}"
      log "Watch resumed; current fingerprint ${last}"
    fi
  done
}

case "${MODE}" in
  watch)
    watch_loop
    ;;
  install-launch-agent)
    install_launch_agent
    ;;
  uninstall-launch-agent)
    uninstall_launch_agent
    ;;
  status-launch-agent)
    status_launch_agent
    ;;
  *)
    run_cycle
    ;;
esac
