# Requirements

## Functional Requirements

- **REQ-01** The system may treat browser-playable local audio files under `public/mymusic/` as valid local music sources.
- **REQ-02** Oversized audio files must be reported clearly in manage diagnostics and deployment logs.
- **REQ-03** Admin users must be able to choose which local music file is active.
- **REQ-04** Public pages must play the selected active local track, not the sorted first file.
- **REQ-05** The selected active file should be stored in a lightweight repo-local metadata file under `public/mymusic/`, not in a database blob.
- **REQ-06** The watcher/deploy script must have an installable macOS launchd mode so it runs automatically after login without manually starting the watch command.
- **REQ-07** The automation must preserve the safe-deploy behavior: deploy from a clean temporary worktree and avoid unrelated dirty source changes.
- **REQ-08** The automation must ignore non-audio clutter such as `.DS_Store`.
- **REQ-09** The system must not attempt to deploy any selected audio file larger than Cloudflare Workers Assets' 25 MiB per-file limit.

## Non-Functional Requirements

- Keep source changes scoped to music/manage/deploy automation.
- Preserve unrelated dirty worktree changes.
- Do not add large dependencies.
- Do not transcode audio unless explicitly requested; first fix should reject or skip oversized files and tell the user what to do.
- Avoid committing or pushing anything unless separately requested.

## Assumptions

- The active metadata file can be `public/mymusic/selection.json`.
- The metadata file can contain `{ "selected_file": "..." }`.
- Supported local music extensions remain browser-native static assets: `.mp3`, `.m4a`, `.aac`, `.ogg`, `.opus`, `.webm`, `.wav`.
- Selected audio files must be under Cloudflare Workers Assets' 25 MiB per-file limit.
- True unattended automation on this Mac should use a LaunchAgent that runs the watcher in the background.
