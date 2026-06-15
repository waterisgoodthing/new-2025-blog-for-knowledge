# Design

## Current Problem

The current workspace can contain unrelated unfinished changes. Running `npm run deploy:full` directly from that workspace may publish those changes along with a music file.

## Target Behavior

Add a shell script, tentatively `scripts/watch-mymusic-deploy.sh`, that runs locally and watches `public/mymusic/`.

When the music folder changes, the script should:

1. Wait for a short debounce period.
2. Normalize music file permissions.
3. Create a temporary clean Git worktree from the current `HEAD`.
4. Copy the active workspace's `public/mymusic/` into that temporary worktree.
5. Run the existing type-check, Cloudflare build, and Wrangler deploy sequence from the temporary worktree.
6. Verify the public static audio URL when a selected audio file exists.
7. Verify the public daily-song API response.
8. Remove the temporary worktree on exit.

## Watch Strategy

Use a portable polling loop instead of requiring `fswatch`.

The loop can compute a fingerprint from file names, sizes, timestamps, and hashes under `public/mymusic/`. When the fingerprint changes, it triggers one deploy after a debounce interval.

## Clean Deployment Strategy

The script should not build from the dirty active workspace.

Preferred strategy:

```text
active workspace
  public/mymusic/song.mp3
  unrelated dirty files

temporary git worktree from HEAD
  clean source from HEAD
  public/mymusic copied from active workspace
```

Deployment runs only in the temporary worktree. This publishes the current stable Git source plus the music folder overlay.

## Safety Controls

- Refuse to run if not inside the repository root.
- Refuse to deploy if `package.json` or `wrangler.toml` is missing in the temporary worktree.
- Print the selected audio file and public URL before verification.
- Keep cleanup traps so temporary worktrees are removed on script exit.
- Do not call `git add`, `git commit`, `git push`, `git reset`, or `git checkout --`.

## Validation Plan

- Shell syntax check: `bash -n scripts/watch-mymusic-deploy.sh`.
- Dry-run mode or no-deploy mode if implemented.
- Confirm the script builds from a temporary directory, not the dirty workspace.
- Confirm it detects the existing `public/mymusic/0250孙燕姿-遇见.mp3`.
- Do not run live deployment unless the user explicitly asks after implementation.
