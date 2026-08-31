# Design

## Root Causes

### Oversized WAV

Cloudflare Workers Assets rejects files over 25 MiB. The current music deploy overlay copies the whole `public/mymusic/` folder, so one 39.8 MiB WAV breaks the entire deploy.

The product decision is to keep format choice flexible for browser-playable audio files. The deployment guard should focus on Cloudflare's 25 MiB per-file limit, not on forcing a single extension.

### No Active Selection

`backend/app/services/local_music_source.py` sorts all supported files and chooses the first one. That made initial implementation deterministic, but it does not support user choice.

### Watcher Not Truly Automatic

`scripts/watch-mymusic-deploy.sh --watch` is only a long-running foreground command. If the user does not start it, no change is detected or deployed.

## Target Behavior

### Source Metadata

Use a small metadata file:

```json
{
  "selected_file": "孙燕姿-遇见.mp3"
}
```

The backend scanner reads this file and selects that file if it exists, has a supported browser-playable audio extension, and is deployable. If it is missing or invalid, diagnostics should report the reason and fall back safely.

### Size Guard

Define a shared deployability rule:

- supported browser-playable audio extension
- file size <= 25 MiB

The backend diagnostics should show all local audio files with:

- file name
- size
- supported extension
- deployable status
- selected status
- warning reason

The deploy script should refuse oversized selected audio files before Cloudflare build/upload. Prefer refusal with a clear error for the selected file, because skipping a selected file would make the API point at a non-existent public asset.

### Manage UI

Update `/manage?tab=music` to list local files and allow selecting the active deployable track. Selection writes `selection.json` through a backend admin endpoint.

Possible endpoint:

```text
PUT /api/music/manage/local-selection
{ "selected_file": "孙燕姿-遇见.mp3" }
```

### LaunchAgent Automation

Add script support:

```bash
scripts/watch-mymusic-deploy.sh --install-launch-agent
scripts/watch-mymusic-deploy.sh --uninstall-launch-agent
scripts/watch-mymusic-deploy.sh --status-launch-agent
```

The LaunchAgent should run:

```bash
/Users/limengyang/2025-blog-public/scripts/watch-mymusic-deploy.sh --watch
```

Logs should go under a predictable local path such as:

```text
/tmp/blog-mymusic-deploy.log
```

## Validation Plan

- Backend unit tests for:
  - selected file wins over sorted first file
  - invalid selection warns and falls back
  - oversized file is rejected or marked non-deployable
- `npx tsc --noEmit`.
- Script checks:
  - `bash -n scripts/watch-mymusic-deploy.sh`
  - no-deploy check reports oversized WAV before deploy
  - LaunchAgent plist generation/install can be inspected without starting deploy if needed
- Public checks after approved deployment:
  - selected track API response
  - selected static audio URL
  - homepage card uses selected track
