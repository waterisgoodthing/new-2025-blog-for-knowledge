# Requirements

## Functional Requirements

- **REQ-01** Watch `public/mymusic/` for added, removed, renamed, or modified audio files.
- **REQ-02** Trigger deployment automatically after a detected music-source change, with debounce to avoid repeated deploys while a file is still being copied.
- **REQ-03** Deploy from a clean temporary worktree or equivalent clean build directory so unrelated dirty source changes are not published.
- **REQ-04** Copy only `public/mymusic/` from the active workspace into the clean deploy workspace before building.
- **REQ-05** Keep using the existing Cloudflare deployment command sequence, equivalent to `npx tsc --noEmit && npm run build:cf && npx wrangler deploy --route 'blog.limengyang.me/*'`.
- **REQ-06** Fix readable permissions for music files before deployment, at minimum ensuring files under `public/mymusic/` are owner/group/world readable.
- **REQ-07** Validate the deployed selected audio URL after deploy when an audio file exists.
- **REQ-08** Validate `https://public-api.limengyang.me/api/music/manage/daily-song/public` after deploy and report whether it returns a track or `null`.
- **REQ-09** The script must log what it is doing and fail loudly when prerequisites are missing.

## Non-Functional Requirements

- Keep changes scoped to `scripts/` and this workflow folder unless implementation evidence proves another file must change.
- Preserve unrelated dirty worktree changes.
- Do not commit, stage, push, or reset user changes.
- Do not require a new large dependency.
- Prefer macOS-compatible shell behavior.

## Assumptions

- The active music source folder is `public/mymusic/`.
- Public frontend deployment is Cloudflare Worker based.
- The safe deployment base should be the current Git `HEAD`, with only `public/mymusic/` overlaid from the active workspace.
- If the public API still returns `null` after static deployment, the likely remaining issue is backend runtime visibility or restart, not the frontend deploy script itself.
