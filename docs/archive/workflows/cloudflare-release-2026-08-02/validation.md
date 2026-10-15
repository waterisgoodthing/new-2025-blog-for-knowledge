# Validation

## Baseline

- Release commit: `202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f` on `refactor/baseline`.
- Local and `mine/refactor/baseline` SHA matched before deployment.
- Cloudflare Wrangler authenticated as the configured account; `CLOUDFLARE_API_TOKEN` is present without exposing its value.
- The previous active Cloudflare version is `23e67efe-d042-435b-a6b7-4236839a8477`, active at 100%, created 2026-07-29T11:52:03Z.
- The deployment source is a detached clean worktree at `/tmp/2025-blog-cf-release-20260802`, resolved to the release commit; `npm ci` completed with no production dependency vulnerabilities.
- The ignored production configuration contains only `NEXT_PUBLIC_API_URL`; the public value is available to the build without recording it in this file.
- Pre-deployment HTTP checks: `https://blog.limengyang.me/` and `https://public-api.limengyang.me/api/health` both returned 200.

## Predeploy Gate

- Ran `npm run predeploy:frontend` in the detached release worktree using Node 24 and the existing public API build value.
- Production dependency audit, Next/OpenNext dependency validation, 23 Vitest files / 64 tests, TypeScript, OpenNext Cloudflare build, and diff hygiene all passed.
- OpenNext generated a Worker bundle from the exact release commit before upload.

## Cloudflare Deployment

- Wrangler uploaded 15 new or modified static assets and reused 277 existing assets.
- Worker: `2025-blog-public`.
- Route: `blog.limengyang.me/*`.
- New active Worker version: `b65cf9b5-3828-4253-891f-420f2597dadc`.
- The deployment command completed successfully; no backend migration, tunnel, DNS, or configuration change was run.

## Public Verification

- The local build, `https://blog.limengyang.me/BUILD_ID`, and `https://2025-blog-public.17527677392.workers.dev/BUILD_ID` all returned `jxcFjdF99TJGSY5szXnXS`.
- Public frontend HTTP checks passed: `/`, `/notes`, `/mistakes`, and `/manage` each returned 200.
- `https://public-api.limengyang.me/api/health` returned 200 with `{"status":"ok"}`.
- Anonymous `/api/auth/me` and `/api/admin/subjects` each returned 401 with `{"detail":"Not authenticated"}`.
- The public page response is served by Cloudflare/OpenNext (`server: cloudflare`, `x-opennext: 1`).

## Conclusion

The clean release commit `202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f` is deployed to Cloudflare Worker version `b65cf9b5-3828-4253-891f-420f2597dadc`. Public frontend delivery and the existing API boundary both passed post-deployment verification.
