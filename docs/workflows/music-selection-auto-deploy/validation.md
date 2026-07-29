# Validation

Validation date: 2026-06-15.

## Backend

- `cd backend && .venv/bin/python -m unittest tests.test_local_music_source`
  - Result: PASS.
  - Coverage: deterministic fallback selection, `selection.json` selected-file priority, invalid selection warning/fallback, oversized-file deployability rejection, missing audio state.

- `cd backend && .venv/bin/python -c "from app.routers import music_manage; from app.services.local_music_source import find_local_music_source; print('music imports ok')"`
  - Result: PASS.

- `launchctl kickstart -k gui/501/com.blog.backend`
  - Result: PASS.
  - Follow-up `GET http://127.0.0.1:8000/api/music/manage/daily-song/public` returned the current deployable local track `孙燕姿-遇见`.

## Frontend

- `npx tsc --noEmit`
  - Result: PASS.

## Deploy Script

- `bash -n scripts/watch-mymusic-deploy.sh`
  - Result: PASS.

- `scripts/watch-mymusic-deploy.sh --check`
  - Result: PASS.
  - Observed supported audio files: `2`.
  - Observed selected deployable audio: `孙燕姿-遇见.mp3`.
  - Observed oversized skip: `孙燕姿 - 天黑黑.wav`.
  - No live deployment was run.

- Temporary oversized selection guard:
  - Setup: temporarily wrote `public/mymusic/selection.json` with `{"selected_file":"孙燕姿 - 天黑黑.wav"}`.
  - Result: PASS.
  - Script exited non-zero and reported that the selected file exceeds Cloudflare Workers' 25 MiB asset limit.
  - Cleanup: restored prior `selection.json` state; final state has no `selection.json`.

## LaunchAgent

- `scripts/watch-mymusic-deploy.sh --install-launch-agent`
  - Result: PASS.
  - Installed `~/Library/LaunchAgents/com.blog.mymusic.deploy.plist`.

- `scripts/watch-mymusic-deploy.sh --status-launch-agent`
  - Result: PASS.
  - State: running.
  - Program: `/bin/zsh -lc "source ~/.zshrc ... scripts/watch-mymusic-deploy.sh --watch"`.
  - Log path: `/tmp/blog-mymusic-deploy.log`.

## Notes

- A first LaunchAgent attempt exposed that Wrangler in a non-interactive launchd environment could not access Cloudflare credentials. The LaunchAgent was updated to start through `zsh -lc` and source `~/.zshrc`, matching the manual deploy environment.

## Public Deployment

Deployment date: 2026-06-15.

- Safe deploy method:
  - Created a temporary clean Git worktree from `HEAD`.
  - Overlaid only music-related frontend files:
    - `src/components/music-card.tsx`
    - `src/app/manage/music-tab.tsx`
    - `src/lib/api/music-manage.ts`
  - Copied only deployable `public/mymusic/` audio assets.
  - Skipped oversized asset `孙燕姿 - 天黑黑.wav` because it is 41,694,083 bytes.
  - Ran `npm ci --prefer-offline --no-audit --no-fund`.
  - Ran `npx tsc --noEmit`.
  - Ran `npm run build:cf`.
  - Ran `npx wrangler deploy --route 'blog.limengyang.me/*'`.

- Deployment result:
  - Result: PASS.
  - Worker version: `6d43afda-2218-4662-aa31-96021cebf766`.
  - Route: `blog.limengyang.me/*`.

- Post-deploy checks:
  - `GET https://public-api.limengyang.me/api/music/manage/daily-song/public`: PASS, returned `孙燕姿-遇见` with `/mymusic/孙燕姿-遇见.mp3`.
  - `HEAD https://blog.limengyang.me/mymusic/%E5%AD%99%E7%87%95%E5%A7%BF-%E9%81%87%E8%A7%81.mp3`: PASS, `HTTP/2 200`, `content-type: audio/mpeg`.
  - `HEAD https://blog.limengyang.me/mymusic/%E5%AD%99%E7%87%95%E5%A7%BF%20-%20%E5%A4%A9%E9%BB%91%E9%BB%91.wav`: PASS, `HTTP/2 404`, confirming the oversized WAV was not uploaded.
  - Live manage JS chunks contain selection UI markers and no old NetEase/candidate-list markers.

## Public Redeploy With Current Workspace

Redeployment date: 2026-06-15.

- Command: `source ~/.zshrc && npm run deploy:full`
- First deploy result: PASS, Worker version `678bff75-84ef-48a0-b752-bc648e8684f5`.
- Cleanup: removed ignored `.DS_Store` files after the first upload log showed `/.DS_Store` and `/mymusic/.DS_Store` were included in static assets.
- Second deploy result: PASS, Worker version `d4690aa9-3013-426d-9223-0d6f1a472a97`.
- Public BUILD_ID after second deploy: `KlhA3CfUDl-Dksu4Iupbl`.
- `HEAD https://blog.limengyang.me/mymusic/%E5%AD%99%E7%87%95%E5%A7%BF-%E9%81%87%E8%A7%81.mp3`: PASS, `HTTP/2 200`, `content-type: audio/mpeg`.
- `GET https://public-api.limengyang.me/api/music/manage/daily-song/public`: PASS, returned `孙燕姿-遇见` with `/mymusic/孙燕姿-遇见.mp3`.
- `GET https://blog.limengyang.me/.DS_Store`: PASS, `404`.
- `GET https://blog.limengyang.me/mymusic/.DS_Store`: PASS, `404`.
