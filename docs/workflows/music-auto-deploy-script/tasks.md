# Tasks

Implementation is blocked until this task list is explicitly approved in conversation.

- [x] **T1** Add `scripts/watch-mymusic-deploy.sh`.
  - Scope: deployment automation only.
  - Completion standard: script watches `public/mymusic/`, debounces changes, creates a clean temporary worktree, overlays only `public/mymusic/`, and runs the existing deploy sequence from the temporary worktree.
  - Completed: 2026-06-15. Added `scripts/watch-mymusic-deploy.sh` with watch/once/check modes, polling fingerprint detection, debounce, clean temporary worktree deployment, and `public/mymusic` overlay.

- [x] **T2** Add safety options and logging.
  - Scope: script behavior.
  - Completion standard: script supports a non-deploy check mode or equivalent safe path, logs detected changes, selected audio file, temporary worktree path, and verification results.
  - Completed: 2026-06-15. Added `--watch`, `--once`, `--check`, `--no-deploy`, interval/debounce options, timestamped logs, prerequisite checks, permission normalization, and explicit selected-file reporting.

- [x] **T3** Add post-deploy verification.
  - Scope: script verification logic.
  - Completion standard: script checks the public static audio URL and `daily-song/public` API response after deployment, and reports whether static deployment and backend detection agree.
  - Completed: 2026-06-15. Added post-deploy checks for `https://blog.limengyang.me/mymusic/<encoded-file>` and `https://public-api.limengyang.me/api/music/manage/daily-song/public`; live checks run only after real deployment.

- [x] **T4** Validate the script without publishing unrelated changes.
  - Scope: local validation.
  - Completion standard: `bash -n` passes; a dry-run/check run proves the script detects `public/mymusic/0250孙燕姿-遇见.mp3`; validation notes record that no live deploy was run unless separately requested.
  - Completed: 2026-06-15. `bash -n` passed; `--check` detected `0250孙燕姿-遇见.mp3`, created a clean temporary worktree, overlaid `public/mymusic`, skipped deploy, and left no temporary worktree behind.

- [x] **T5** Update workflow evidence.
  - Scope: `validation.md` and optional `handoff-prompt.md`.
  - Completion standard: validation commands, results, and any limitations are recorded.
  - Completed: 2026-06-15. Updated `validation.md` with command results, no-deploy limitation, permission state, and cleanup fix notes; updated README status.
