# Tasks

Implementation is blocked until this task list is explicitly approved in conversation.

- [x] **T1** Update homepage music card data source.
  - Scope: `src/components/music-card.tsx`.
  - Completion standard: card loads `getPublicDailySong()` and displays the local track when available.
  - Completed: 2026-06-15. `MusicCard` now loads `getPublicDailySong()` from the local single-track public endpoint and displays the returned title/artist/artwork.

- [x] **T2** Update playback behavior for public full-track audio.
  - Scope: `src/components/music-card.tsx`.
  - Completion standard: play button uses the local `preview_url`; no fake fallback track is treated as playable.
  - Completed: 2026-06-15. The play button now uses the local `preview_url`, disables itself when no track exists, and no longer treats the `Close To You` fallback as playable.

- [x] **T3** Validate frontend type safety and public asset/API availability.
  - Scope: validation only.
  - Completion standard: TypeScript check passes or any pre-existing failure is documented; public API and static audio checks are recorded.
  - Completed: 2026-06-15. `npx tsc --noEmit` passed; public daily-song API returned the local track; public static audio returned `HTTP 200 audio/mpeg`.

- [x] **T4** Record workflow evidence.
  - Scope: `validation.md`.
  - Completion standard: implementation and validation evidence are recorded.
  - Completed: 2026-06-15. Validation evidence and source-inspection notes recorded in `validation.md`.
