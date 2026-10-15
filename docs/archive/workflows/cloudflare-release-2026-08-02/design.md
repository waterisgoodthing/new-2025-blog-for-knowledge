# Design

The existing deploy command is `npm run deploy:full`. It first runs the frontend release gate, then executes Wrangler with the existing `blog.limengyang.me/*` route. The target Worker is `2025-blog-public` from `wrangler.toml`.

The release source must remain clean and match `mine/refactor/baseline`. The frontend-only gate intentionally does not require the separate backend predeploy database URLs; backend data remains served by the existing public API tunnel.

After Wrangler reports a new version, verification will compare the public site response with the local release build, check the public API health endpoint, and validate unauthenticated public/admin boundaries without credentials.
