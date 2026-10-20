# Tasks

Implementation was approved by the user in conversation on 2026-06-14. Execute one item at a time and update this file immediately after each item is completed.

## Phase 0: Source Inspection

- [x] **T0-01** Inspect existing music backend and frontend contracts.
  - Scope: `backend/app/services/netease_service.py`, `backend/app/routers/music_manage.py`, `src/lib/api/music-manage.ts`, `src/app/music/page.tsx`, `src/app/manage/music-tab.tsx`.
  - Completion standard: confirm which existing response shapes can be preserved.
  - Completed: 2026-06-14. Existing `DailySongItem` shape can be preserved by returning local file data with `preview_url=/mymusic/<file>` and `netease_url=null`; `/music` can mostly reuse its current playback flow, while `/manage` needs a local-source status UI.

- [x] **T0-02** Confirm local source folder status.
  - Scope: `public/mymusic/`.
  - Completion standard: create the folder if absent, do not add audio content unless provided by the user.
  - Completed: 2026-06-14. Created `public/mymusic/`; it contains no audio files yet.

## Phase 1: Backend Local Source

- [x] **T1-01** Add a local music source scanner.
  - Scope: backend music service layer.
  - Completion standard: scans `public/mymusic/`, finds valid browser-playable audio files, returns deterministic single-track status and warnings.
  - Completed: 2026-06-14. Added `backend/app/services/local_music_source.py` and `backend/tests/test_local_music_source.py`; scanner selects one deterministic audio file, ignores non-audio files, and reports missing/multiple-file warnings.

- [x] **T1-02** Adapt public/manage music endpoints to use local single-track data.
  - Scope: `backend/app/routers/music_manage.py` and related service calls.
  - Completion standard: daily-song public/manage endpoints return the local track object or null; diagnostics reports local source state.
  - Completed: 2026-06-14. Public/manage daily-song endpoints now return the scanned local track or `null`; history returns no generated list; diagnostics reports `source_type=local_single`, source directory, file count, selected file, and warnings.

- [x] **T1-03** Disable external NetEase actions from active endpoint behavior.
  - Scope: sync/generate/config endpoints as needed.
  - Completion standard: endpoints no longer claim NetEase is required for the active music page; unsupported actions return clear messages or are removed from UI use.
  - Completed: 2026-06-14. NetEase config now reports local source status, health checks `public/mymusic`, source rules and candidates return empty read data, and external config/rule/sync mutations return 410 with local-source guidance.

## Phase 2: Frontend Local Management

- [x] **T2-01** Update frontend music API types for local source diagnostics.
  - Scope: `src/lib/api/music-manage.ts`.
  - Completion standard: types include local source fields without requiring NetEase fields.
  - Completed: 2026-06-14. Extended music manage API types with `source_type`, `source_dir`, `selected_file`, `local_file_count`, `warnings`, and related local-source fields while preserving old response fields for compatibility.

- [x] **T2-02** Simplify `/manage` music tab to local single-track management.
  - Scope: `src/app/manage/music-tab.tsx`.
  - Completion standard: UI shows `public/mymusic` status, detected track, playback, warnings, and no primary NetEase candidate/config workflow.
  - Completed: 2026-06-14. Replaced the NetEase/candidate/manual-list tab UI with a local single-source status panel, local playback preview, warnings, and a source refresh action.

- [x] **T2-03** Update public `/music` page if needed.
  - Scope: `src/app/music/page.tsx`.
  - Completion standard: public page plays the local track and handles null source cleanly.
  - Completed: 2026-06-14. Public music page now loads only the local single track, uses local playback controls, removes history/NetEase UI, and shows a local-file empty state.

## Phase 3: Validation

- [x] **T3-01** Run TypeScript validation.
  - Command: `npx tsc --noEmit`.
  - Completion standard: pass or document first relevant failure.
  - Completed: 2026-06-14. `npx tsc --noEmit` passed.

- [x] **T3-02** Run frontend build validation.
  - Command: `npm run build`.
  - Completion standard: pass or document first relevant failure.
  - Completed: 2026-06-14. `npm run build` passed; only baseline-browser-mapping freshness and Node deprecation warnings were emitted.

- [x] **T3-03** Run backend import/start checks.
  - Completion standard: music router/service imports without errors.
  - Completed: 2026-06-14. `tests.test_local_music_source` passed and `app.routers.music_manage` / `app.services.local_music_source` imported successfully.

- [x] **T3-04** Browser-check manage and public music pages.
  - Completion standard: local source status and public playback/empty state are verified.
  - Completed: 2026-06-14. Browser checked isolated local frontend/backend on `http://127.0.0.1:3025` + `http://127.0.0.1:8011`: `/music` showed the local empty state with no NetEase text, and `/manage?tab=music` showed the local source panel, `public/mymusic`, empty state, and no NetEase text.

- [x] **T3-05** Record validation evidence.
  - Scope: `validation.md`.
  - Completion standard: commands, browser routes, and limitations are recorded.
  - Completed: 2026-06-14. Validation evidence recorded in `validation.md`, including command checks, isolated local browser checks, source state, and the real-audio playback limitation.
