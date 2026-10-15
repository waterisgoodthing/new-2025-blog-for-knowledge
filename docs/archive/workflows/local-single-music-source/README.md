# Local Single Music Source

## Goal

Replace the NetEase candidate-pool daily song workflow with one local single-track source. The only audio source is the `public/mymusic/` folder, and the music experience should play that single local track instead of syncing, generating, or choosing from external music APIs.

## Touched Domains

- `music`: local single-track source, public playback data, music page behavior.
- `manage`: music management page simplified to local-file status and validation.
- `backend`: music management/public endpoints adapted away from NetEase candidate sync.
- `shared infrastructure`: frontend API contract updates for music data.

## Current Status

Planning only. Implementation must not start until `tasks.md` is approved in conversation.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Approval Gate

Implementation is blocked until the user explicitly approves the task list in `tasks.md`.
