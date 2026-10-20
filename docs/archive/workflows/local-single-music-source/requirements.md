# Requirements

## Functional Requirements

- **REQ-01** The music source must be local only. No NetEase, official cloud media API, or third-party music API may be required for playback.
- **REQ-02** The only audio source folder is `public/mymusic/`.
- **REQ-03** The application should support one active playable track at a time.
- **REQ-04** Music management should show the local source state instead of NetEase config, candidate sync, source rules, or API health.
- **REQ-05** The public `/music` page should play the local track when a valid audio file exists.
- **REQ-06** If no valid file exists, public and manage UIs should show a clear empty/error state.
- **REQ-07** The backend should expose a stable public response shape compatible with the music page, while marking unavailable external fields as null.
- **REQ-08** The solution should minimize local storage use by avoiding duplicate copies, transcoding caches, generated derivatives, or database blobs.
- **REQ-09** Static assets referenced by UI must exist under `public/`.

## Non-Functional Requirements

- Keep changes scoped to music/manage/backend music integration.
- Preserve unrelated dirty worktree changes.
- Avoid database model changes unless source inspection proves them necessary.
- Keep NetEase-specific code either removed from active UI paths or isolated as unused legacy code; do not deepen the dependency.

## Assumptions

- The intended folder path is `public/mymusic/`.
- Exactly one audio file should be considered active. If multiple valid files exist, the implementation should choose a deterministic file and surface a warning in management.
- Supported audio extensions should be browser-native static assets: `.mp3`, `.m4a`, `.aac`, `.ogg`, `.opus`, `.webm`, `.wav`.
- Optional metadata can be inferred from the filename when no sidecar metadata exists.
