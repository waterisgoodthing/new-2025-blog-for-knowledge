# Design

## Root Cause

The backend and public static asset path are now correct, but the homepage music card still uses the old playlist flow:

```text
MusicCard -> getPlaylist() -> /api/music/playlist -> fallback Close To You
```

The current local single-track source is exposed through:

```text
MusicCard -> getPublicDailySong() -> /api/music/manage/daily-song/public
```

## Target Flow

Update `src/components/music-card.tsx` to load `getPublicDailySong()` from `src/lib/api/music-manage.ts`.

Use the returned `DailySongItem` as the card track:

- `title`: local file stem.
- `artist`: null or local source label.
- `preview_url`: `/mymusic/<file>`.
- `artwork_url`: optional, if later provided.

Because the page runs on `blog.limengyang.me`, a root-relative `/mymusic/<file>` resolves to the public static asset host and allows public playback.

## Fallback Behavior

If the endpoint returns `null` or fails, keep a visible but non-playable placeholder. Do not show a fake active track as if it could play.

## Validation Plan

- `npx tsc --noEmit`.
- Public checks:
  - `GET https://public-api.limengyang.me/api/music/manage/daily-song/public`.
  - `HEAD https://blog.limengyang.me/mymusic/<encoded-file>`.
- Browser check `/` after local or deployed build if available.
