# Home Music Local Playback Fix

## Goal

Make the homepage music card use the current local single-track music source and allow public visitors to play the full uploaded local audio.

## Touched Domains

- `home`: homepage floating music card.
- `music`: local single-track public playback.
- `shared infrastructure`: frontend public API/static asset URL handling.

## Current Status

Planning only. Implementation is blocked until `tasks.md` is explicitly approved in conversation.

## Evidence

- `https://public-api.limengyang.me/api/music/manage/daily-song/public` returns the local track JSON.
- `https://blog.limengyang.me/mymusic/0250%E5%AD%99%E7%87%95%E5%A7%BF-%E9%81%87%E8%A7%81.mp3` returns `HTTP 200` with `content-type: audio/mpeg`.
- `src/components/music-card.tsx` still calls the legacy playlist API and falls back to `Close To You`.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Approval Gate

Implementation must not start until the user explicitly approves the task list in `tasks.md`.
