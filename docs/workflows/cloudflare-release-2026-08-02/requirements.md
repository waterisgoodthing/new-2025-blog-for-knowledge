# Requirements

1. The local deployment commit must exactly match the pushed `refactor/baseline` branch and have a clean worktree before the release gate runs.
2. `npm run predeploy:frontend` must pass before any Wrangler upload.
3. The Worker deployment must target only `blog.limengyang.me/*`.
4. Deployment must not run database migrations or change backend, tunnel, DNS, secrets, or auth settings.
5. Post-deployment verification must include public site HTTP success, public API health, and an unauthenticated admin API denial.
6. The final Cloudflare version, route, release commit, and verification results must be recorded in `validation.md`.
