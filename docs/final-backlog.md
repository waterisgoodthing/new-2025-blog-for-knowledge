# Final Backlog

## Backlog Policy

Items in this document are deferred unless explicitly marked as blocking. They should not be treated as current acceptance blockers for the System Freeze & Acceptance Sprint.

| Item | Priority | Blocks Current Use | Suggested Batch | Risk | Suggested Validation |
| --- | --- | --- | --- | --- | --- |
| ProviderProfile / ModelProfile / RoutingRule database persistence | P2 | No | Batch 13A | Config drift between code policy and production needs; migration scope expansion. | Migration upgrade/downgrade, typed API contract tests, admin-only CRUD tests, no-secret persistence scan. |
| `ai_usage_daily` persistence | P2 | No | Batch 13B | Daily aggregates can double-count if not idempotent; timezone ambiguity. | Fixture log aggregation tests, idempotent upsert tests, timezone boundary tests. |
| Actual token usage persistence | P2 | No | Batch 13B | Provider response formats vary; missing usage could be mistaken for zero. | Provider response fixture tests; unknown/null assertions for missing usage. |
| Estimated cost calculation | P2 | No | Batch 13B | Misleading billing if prices are stale or guessed. | Price table version tests, explicit estimated/actual source fields, UI copy review. |
| Budget / quota enforcement | P2 | No for personal use | Batch 13C | False positives can block legitimate personal workflow; false negatives can allow runaway usage. | Limit policy tests, boundary tests, admin override tests, provider failure simulation. |
| Real provider probe | P2 | No | Batch 13D | Probe cost/rate limits; probe success may be confused with business success. | Controlled no-sensitive prompt, before/after health event evidence, separate mock vs true-provider labels. |
| Health event table | P2 | No | Batch 13D | Event retention and sensitive provider error text leakage. | Migration tests, safe error truncation tests, retention policy tests. |
| Automatic circuit breaker / cooldown / provider temporary disablement | P2 | No | Batch 13E | Incorrect cooldown can disable the only working provider or overuse fallback. | Mock provider failure matrix, cooldown clock tests, explanatory fallback UI tests. |
| Provider/routing online editing | P3 | No | Batch 14A | Admin UI can expose secret-like config or create invalid routing. | Admin-only route tests, form validation tests, no-secret response scan, browser edit/revert flow. |
| Prompt admin | P3 | No | Batch 14B | Prompt edits can change output contracts without test coverage. | Prompt registry contract tests, approval workflow tests, rollback tests. |
| Prompt A/B testing | P3 | No | Batch 14C | Hard to interpret results with small personal dataset; can create unstable output. | Experiment assignment determinism, audit logging, off switch, effect report sanity checks. |
| Prompt hot update | P3 | No | Batch 14C | Runtime prompt changes can bypass code review and versioning. | Versioned publish/rollback tests, audit logs, cache invalidation tests. |
| Prompt effectiveness evaluation | P3 | No | Batch 14D | Evaluation may incentivize superficial metrics; needs fixture dataset. | Golden fixture set, regression report, manual review sample. |
| Complete provider token streaming audit | P2 | No | Stream Lifecycle Patch | Client disconnect, parser failure, and partial output semantics are complex. | Mock generator tests, controlled browser disconnect, true provider stream proof, sensitive partial-output scan. |
| Longer browser-side regression coverage | P2 | No | Acceptance Hardening | Manual acceptance can miss route-specific regressions. | Playwright smoke suite for public/admin routes with auth fixture and network assertions. |
| Legacy source dead code cleanup | P3 | No | Cleanup Batch | Removing compatibility code can break old bookmarks or hidden flows. | Route scan, build, browser smoke, dead link check. |
| `/api/folders` admin boundary review | P2 | No | Security Review Batch | `/notes` currently requests `/api/folders` anonymously and receives 200; this may be intended public metadata or an overexposure. | Backend route audit, anonymous response field scan, product decision on public folder metadata. |
| Local production CORS configuration review | P2 | No | Setup Hardening | Fresh local alternate ports can fail preflight unless `ALLOWED_ORIGINS` is updated correctly. | `npm run setup` / `.env.example` review, browser preflight tests for documented local ports. |
| httpOnly cookie session check architecture cleanup | P2 | No | Auth Cleanup | Cross-origin frontend/backend auth can be confusing; cookie path `/api` is correct but setup docs need clarity. | Auth login/logout browser tests, cookie attribute inspection, setup doc validation. |
| Batch 8 true AI/OCR provider proof | P2 | No | Provider Proof Batch | Mock/fake adapter success can be mistaken for true provider OCR success. | One controlled non-sensitive image proof, Run/call-log evidence, explicit provider/model/fallback record. |
| AI Gateway test warning cleanup | P3 | No | Test Hygiene | AsyncMock warning can hide future async misuse if warnings grow. | Targeted pytest with warnings-as-errors for `test_ai_gateway.py`. |
| Existing public manage links review | P3 | No | UX Cleanup | Public pages show a visible `管理` link that routes to login; acceptable for personal site, but may be visually noisy. | Product decision, anonymous route browser check. |

## Recommended Next Order

1. `/api/folders` boundary review and local production CORS docs, because they are small and acceptance-adjacent.
2. Browser regression smoke suite, because it makes future freezes cheaper.
3. Token/cost persistence only after provider response usage fields are confirmed.
4. Real provider probe and health event table only after deciding acceptable probe cost/rate limits.
5. Provider/routing online editing and Prompt admin only after the read-only governance surface stays stable in real use.
