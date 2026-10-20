# Design

The audit will use the application's real locally running frontend, preserving normal authentication boundaries. It will enumerate routes from the project, discover the actual frontend port, then use browser automation to render and inspect representative accessible routes at 1440x900, 1280x800, and 390x844.

Artifacts are observational only: screenshots under `docs/ui-review/artifacts/` and four Markdown inventories/reports under `docs/ui-review/`. Login-protected pages are tested only with a user-supplied non-production account; no session fabrication, authentication bypass, or production credential use is permitted.
