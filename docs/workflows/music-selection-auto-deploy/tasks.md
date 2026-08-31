# Tasks

Implementation is blocked until this task list is explicitly approved in conversation.

- [x] **T1** Add backend local music metadata and deployability model.
  - Scope: `backend/app/services/local_music_source.py`, tests.
  - Completion standard: scanner reads `selection.json`, reports file sizes/deployability, rejects or warns on unsupported/oversized files, and unit tests cover selected/invalid/unsupported/oversized cases.
  - Completed: 2026-06-15. Added local file metadata, `selection.json` read/write, Cloudflare 25 MiB deployability checks, selected-file priority, unsupported/oversized warnings, and unit coverage.

- [x] **T2** Add backend admin endpoint for active music selection.
  - Scope: `backend/app/routers/music_manage.py`.
  - Completion standard: authenticated admin can set the selected local audio file; invalid, missing, unsupported, or oversized files are rejected with clear messages.
  - Completed: 2026-06-15. Added `PUT /api/music/manage/local-selection` with file-name, existence, supported-extension, and 25 MiB checks; diagnostics/config now expose selected metadata and file list.

- [x] **T3** Update music management UI for selection.
  - Scope: `src/app/manage/music-tab.tsx`, `src/lib/api/music-manage.ts`.
  - Completion standard: UI lists local audio files, reports unsupported files separately, marks oversized files, and lets admin select one deployable active track.
  - Completed: 2026-06-15. Extended API types and manage UI to list local files, show size/deployability, expose selected state, and call the local-selection endpoint.

- [x] **T4** Harden safe deploy script against oversized files and clutter.
  - Scope: `scripts/watch-mymusic-deploy.sh`.
  - Completion standard: script ignores `.DS_Store`, refuses deploy when the selected audio file is over 25 MiB, and prints a clear remediation message.
  - Completed: 2026-06-15. Script now honors selected/deployable audio, skips oversized unselected assets before Cloudflare upload, refuses oversized selected assets, and ignores non-audio clutter during overlay.

- [x] **T5** Add launchd automation commands.
  - Scope: `scripts/watch-mymusic-deploy.sh` and generated LaunchAgent plist.
  - Completion standard: script supports install/uninstall/status for a user LaunchAgent that runs the watcher automatically after login.
  - Completed: 2026-06-15. Added `--install-launch-agent`, `--uninstall-launch-agent`, and `--status-launch-agent` commands for `com.blog.mymusic.deploy`.

- [x] **T6** Validate without publishing unrelated dirty changes.
  - Scope: tests and local checks.
  - Completion standard: backend tests pass, `npx tsc --noEmit` passes or pre-existing failures are documented, `bash -n` passes, oversized WAV behavior is verified.
  - Completed: 2026-06-15. Backend tests/import checks passed, TypeScript passed, script syntax/check mode passed, oversized selected WAV was rejected, and LaunchAgent status is running.

- [x] **T7** Record workflow evidence.
  - Scope: `validation.md`.
  - Completion standard: validation evidence and any deployment limits are recorded.
  - Completed: 2026-06-15. Recorded backend, frontend, deploy-script, oversized-file, and LaunchAgent validation evidence.
