# Validation

Validation date: 2026-06-15.

## Code Validation

- `npx tsc --noEmit`
  - Result: PASS.

## Public Runtime Evidence

- `GET https://public-api.limengyang.me/api/music/manage/daily-song/public`
  - Result: PASS.
  - Response includes local track `0250孙燕姿-遇见` and `preview_url` `/mymusic/0250孙燕姿-遇见.mp3`.

- `HEAD https://blog.limengyang.me/mymusic/0250%E5%AD%99%E7%87%95%E5%A7%BF-%E9%81%87%E8%A7%81.mp3`
  - Result: PASS.
  - Status: `HTTP/2 200`.
  - Content-Type: `audio/mpeg`.
  - Cache: Cloudflare `HIT`.

## Source Inspection

- `src/components/music-card.tsx` now uses `getPublicDailySong()` instead of the legacy playlist API.
- The card no longer treats the old `Close To You` fallback as a playable track.
- The play button uses the returned local `preview_url` and is disabled when no playable local track exists.

## Not Run

- Browser playback click was not rechecked in this turn.

## Public Deployment

Deployment date: 2026-06-15.

- Safe deploy method:
  - Created a temporary clean Git worktree from `HEAD`.
  - Overlaid only `src/components/music-card.tsx` and `public/mymusic/` from the active workspace.
  - Copied `.env.production` and generated temporary `next-env.d.ts`.
  - Ran `npm ci --prefer-offline --no-audit --no-fund`.
  - Ran `npx tsc --noEmit`.
  - Ran `npm run build:cf`.
  - Ran `npx wrangler deploy --route 'blog.limengyang.me/*'`.

- Deployment result:
  - Result: PASS.
  - Worker version: `f1c10dae-f937-4e02-bbf7-894d6de54a47`.
  - Route: `blog.limengyang.me/*`.

- Post-deploy checks:
  - `GET https://public-api.limengyang.me/api/music/manage/daily-song/public`: PASS, returned local track JSON.
  - `HEAD https://blog.limengyang.me/mymusic/0250%E5%AD%99%E7%87%95%E5%A7%BF-%E9%81%87%E8%A7%81.mp3`: PASS, `HTTP/2 200`, `content-type: audio/mpeg`.
  - Downloaded live homepage JS chunks and searched them:
    - New local music markers: present.
    - Old `Close To You` / `/api/music/playlist` markers: absent.
