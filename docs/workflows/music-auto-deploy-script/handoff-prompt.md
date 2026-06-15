# Handoff Prompt

Implement the approved `music-auto-deploy-script` workflow in `/Users/limengyang/2025-blog-public`.

Follow the repository rules in `AGENTS.md`:

- Preserve unrelated dirty worktree changes.
- Do not deploy from the dirty active workspace.
- Do not commit, stage, push, reset, or revert user changes.
- Keep changes scoped to `scripts/` and `docs/workflows/music-auto-deploy-script/` unless evidence requires otherwise.

Approved design summary:

- Add `scripts/watch-mymusic-deploy.sh`.
- Watch `public/mymusic/`.
- On change, debounce, normalize permissions, create a temporary clean Git worktree from `HEAD`, overlay only `public/mymusic/`, run the existing Cloudflare deploy sequence there, verify public static audio and `daily-song/public`, then clean up.
