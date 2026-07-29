# Music Auto Deploy Script

## Goal

Create a safe shell-based watcher for `public/mymusic/` so music file changes can be deployed without publishing unrelated dirty worktree changes.

## Touched Domains

- `music`: source audio files under `public/mymusic/`.
- `shared infrastructure`: deployment automation and public static asset verification.
- `deploy`: Cloudflare Worker frontend deployment flow.

## Current Status

Implemented and locally validated without live deployment. The script exists at `scripts/watch-mymusic-deploy.sh`; real deployment must be started explicitly by running the script in deploy mode.

## Related Workflow

- [`../local-single-music-source/`](../local-single-music-source/) defines the current local single-track music source behavior.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Approval Gate

Task list was approved in conversation on 2026-06-15. Local no-deploy validation is recorded in `validation.md`.
