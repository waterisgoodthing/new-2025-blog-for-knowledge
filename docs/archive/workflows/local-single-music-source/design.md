# Design

## Current Problem

The existing music flow is built around NetEase API configuration, source rules, candidate sync, daily-song generation, and history. That architecture fails when external APIs are unavailable and is now out of scope because the user wants one local source only.

## Target Behavior

`public/mymusic/` becomes the single source of truth:

```text
public/mymusic/
  song.mp3
  optional-cover.webp
  optional-metadata.json
```

Minimum viable source requires only one audio file. Optional metadata may later provide title, artist, album, cover, and reason, but the first implementation can infer title from filename.

## Backend Contract

Keep the existing public daily song endpoints where possible so the public `/music` page does not need a route-level rewrite:

- `GET /api/music/manage/daily-song/public`
- `GET /api/music/manage/history/public`
- `GET /api/music/manage/daily-song`
- `GET /api/music/manage/diagnostics`

The service should scan `public/mymusic/` and return a single song-like object:

```json
{
  "id": 1,
  "date": "2026-06-14",
  "title": "song",
  "artist": null,
  "album": null,
  "artwork_url": null,
  "preview_url": "/mymusic/song.mp3",
  "netease_url": null,
  "recommendation_reason": null
}
```

If no audio file exists, return `null` for public daily-song and diagnostic fields explaining the missing source.

## Manage UI

Replace the NetEase-heavy music management surface with a local-source status panel:

- `public/mymusic` source path.
- Detected audio file.
- File URL.
- Playback preview.
- Warnings for zero files or multiple files.
- Removed/hidden NetEase config, candidate pool sync, and source rules from the primary UI.

## Storage Strategy

The lowest-storage path is to store only the original audio file under `public/mymusic/` and reference it directly. Do not duplicate it into backend uploads, database blobs, generated caches, or daily history copies.

## Validation Plan

- TypeScript validation: `npx tsc --noEmit`.
- Frontend build validation: `npm run build`.
- Backend import check for music router/service.
- Browser check:
  - `/manage?tab=music` shows local source state.
  - `/music` loads and plays local track when a valid file is present.
  - Empty state is clear when `public/mymusic/` has no audio file.
