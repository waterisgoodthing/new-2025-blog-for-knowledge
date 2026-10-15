# Music Selection Auto Deploy

## Goal

Fix the local music workflow so large files cannot break Cloudflare deployment, the admin can choose the active local track, and music deployment can run automatically without manually starting the watcher each time.

## Touched Domains

- `music`: local source scanning and selected active track.
- `manage`: music management selection UI and warnings.
- `deploy`: safe music deployment limits and automation.
- `shared infrastructure`: macOS launchd automation for the local watcher.

## Current Status

Planning only. Implementation is blocked until `tasks.md` is explicitly approved in conversation.

## Evidence

- Cloudflare Workers Assets rejected `public/mymusic/孙燕姿 - 天黑黑.wav` because the file is 39.8 MiB and Workers assets support only files up to 25 MiB.
- Current scanner picks the sorted first supported audio file, so the user cannot choose which song is active.
- Current watcher script is only automatic after it is manually started; it is not installed as a background launchd service.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Approval Gate

Implementation must not start until the user explicitly approves the task list in `tasks.md`.
