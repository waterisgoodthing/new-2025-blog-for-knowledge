# Requirements

## Functional Requirements

- **REQ-01** The homepage music card must use the local single-track public endpoint, not the legacy playlist endpoint.
- **REQ-02** Public visitors must be able to play the full uploaded local audio from the homepage card.
- **REQ-03** The homepage card must display the local track title instead of the `Close To You` fallback when a local track exists.
- **REQ-04** If no local track exists, the card should remain safe and non-broken, with no fake playable state.
- **REQ-05** Playback should use the public static asset URL for `/mymusic/<file>`.

## Non-Functional Requirements

- Keep changes scoped to the homepage music card and existing music API client if needed.
- Do not change backend behavior unless source inspection proves it is required.
- Preserve unrelated dirty worktree changes.
- Do not redesign unrelated homepage UI.

## Acceptance Criteria

- The card title on `/` shows the local file-derived title.
- Clicking play starts the uploaded track for anonymous/public visitors.
- The public static music file remains reachable with `HTTP 200`.
- TypeScript validation passes for touched frontend code.
