# Handoff Prompt

Implement the approved `music-selection-auto-deploy` workflow in `/Users/limengyang/2025-blog-public`.

Key constraints:

- Preserve unrelated dirty worktree changes.
- Do not deploy unless explicitly requested.
- Keep changes scoped to music/manage/deploy automation.
- Respect Cloudflare Workers Assets' 25 MiB per-file limit.
- Add true macOS LaunchAgent automation so the watcher can run without manual foreground commands.
