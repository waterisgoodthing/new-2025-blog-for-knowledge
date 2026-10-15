# Week 4 Gate — Independent Recheck of `quality-reassessment.md`

Date: 2026-09-26
Mode: main agent evidence-verification activity (read-only), with direct source inspection and targeted reproduction.
Purpose: independently verify the external reassessment `quality-reassessment.md` (which judges M4 **FAIL**) and correct the earlier Gate verdict if warranted.

## Verdict

**The reassessment is substantially correct. The earlier Week 4 Gate verdict of `PARTIAL` is
superseded: Week 4 Gate is `FAIL`.**

Reason: F01, F02, F03 are reproducible defects in Week 4 deliverable scope, and F04 is a
coverage gap against a named requirement; these are not mere authorization-scoped
`NOT_VERIFIED` items. F05–F08 are valid secondary defects/overclaims. My earlier `PARTIAL`
was too lenient because I treated the CI job as "locally reproduced" using scratch DBs, which
changed the as-configured variable (`blog_db`), and because I accepted the PR-15 "concurrent
challenges" acceptance on insert-only tests.

## Independent verification of each finding

| ID | Claim | My independent check | Result |
|---|---|---|---|
| F01 | CI's three DB jobs use `blog_db`, which the repo's own safety guards reject | `.github/workflows/ci.yml:50,60,119,130,217,231` use `blog_db`; `alembic/env.py:57-60` calls `require_migration_target`; `scratch_db_safety.require_migration_target`/`require_scratch_database` both REFUSE `blog_db` (reproduced in-repo: migration refused, scratch refused) | **CONFIRMED (HIGH)** |
| F02 | PR-15 makes CLI passkey options touch DB, and `cli.py` creates a new event loop per request while reusing one AsyncEngine → cross-loop pool error | `cli.py:157-159` creates one `engine`; `cli.py:162-173` `_run_on_db` creates+closes a new loop per call; `do_GET` options now calls `generate_registration_options(session, ...)` (DB). asyncpg pooled connection bound to first loop → second request fails | **CONFIRMED (HIGH, regression)** |
| F03 | Multi-ceremony interference: verify selects latest unbound challenge, not the one matching the assertion | `webauthn_challenge_service.get_valid_challenge:100-103` orders by `created_at desc` limit 1; `passkey_service.verify_authentication:239-246` uses it and passes that challenge as `expected_challenge`. Generating B makes pending A fail. Legacy in-memory code overwrote `"current"`, so this preserves old behavior but violates the PR-15 acceptance "concurrent ceremonies do not overwrite/interfere" | **CONFIRMED (HIGH, acceptance gap)** |
| F04 | E2E-03/04 do not exercise the R22b business flows | `tests/e2e/03-capture.spec.ts` only checks capture-mode tabs/upload entry; `tests/e2e/04-review-flow.spec.ts` only checks review header/empty-state. No wrong-answer→draft, no re-answer→review record; no seed/backend readback. R22b (`requirements.md`) expects the business chain | **CONFIRMED (HIGH, coverage gap)** |
| F05 | OCR taxonomy does not map real lower-layer exceptions | `ai_service.py:130` raises `RuntimeError("AI API error (<status>): <resp.text>")`; `_parse_json_response:139-140` raises `RuntimeError("Failed to parse AI response")`; both surface via `capture_recognition.py:142-158` through `categorize_provider_error`, which only sniffs auth/model/timeout substrings → native timeout (empty `str(ReadTimeout)`) and malformed JSON fall to `provider_error`/`unknown` | **CONFIRMED (MEDIUM)** |
| F06 | Account throttle dict grows without bound; no username length limit | `login_throttle.py:118-125` stores any `account` key with no eviction; `_evict_expired` applies to IPs only; accounts intentionally do not decay (W4-E04). `schemas/auth.py` `LoginRequest.username` has no length bound. Nonexistent usernames persist | **CONFIRMED (MEDIUM)** |
| F07 | Full OCR log chain is not sanitized (pre-existing) | `ai_service.py:130` embeds `response.text`; `:198` logs `err_str[:100]`; `:193,207` store error strings passed onward to `ai_gateway` run/log writers. PR-14 sanitized only the two capture adapters | **CONFIRMED (HIGH security debt, pre-existing)** |
| F08 | Unwired backfill counted as PASS | `week4-gate-matrix.md` row reads `PASS (prospective)`; helper is tested but no production confirmation endpoint calls it | **CONFIRMED (MEDIUM, overclaim)** |

## Corrections to my earlier artifacts

- `week4-gate-matrix.md` / `week4-gate-summary.md` / `week4-technical-report.md`: overall verdict changed `PARTIAL` → **FAIL**; CI job "locally reproduced" downgraded (as-configured CI would be blocked by F01); PR-15 concurrency and PR-19 creation-backfill acceptance corrected; PR-14/16/17 reassessed.
- `TRACKING.md`: overall status changed to `FAIL`.
- PR-15 as-configured is **FAIL** (CLI regression F02 + ceremony interference F03), not PASS.
- PR-17 as-configured is **FAIL** (F01 CI blocker + F04 coverage), not PASS_WITH_NOTES.

## Independent reproduction (my own probes, read-only)

Probe: `evidence/gate/recheck_probes.py` → raw output `evidence/gate/recheck-probes.log`
(scratch DB `astra_week4_pr15`; refused to run against any non-`astra_week4_*` target).

- **F01 reproduced**: `require_migration_target(".../blog_db")` → REFUSED; `require_scratch_database(".../blog_db")` → REFUSED. CI's three jobs target `blog_db` → deterministically blocked.
- **F02 reproduced exactly**: one AsyncEngine + a new event loop per call: request 1 → `1`; request 2 → `RuntimeError: ... got Future ... attached to a different loop`. Matches `cli.py:157-173` pattern.
- **F03 mechanism reproduced**: `store A → get_valid = A`; `store B → get_valid = B` while A is still unconsumed. `passkey_service.verify_authentication` passes the selected record as `expected_challenge`, so a fresh A assertion is checked against B → interference.
- **F05 reproduced (nuance recorded)**: `categorize_provider_error` on the wrapped final error `"All AI providers failed. Trail: provider: "` → `unknown`, and on `"Failed to parse AI response: ..."` → `unknown`. NOTE: the literal string `"ReadTimeout"` maps to `provider_timeout` (substring match); the gap is that the wrapped/empty-string forms lose it. So the finding holds for wrapped errors and malformed JSON, and is conditional for native timeouts depending on `str(exc)`.
- **F06 reproduced**: one 100,000-char username creates and retains an account key; unrelated failures do not evict it; no length/capacity bound.

F04/F07/F08 are control-flow/source facts (E2E spec bodies; `ai_service.py:130,198`; gate matrix row) already confirmed above.

## Verdict after my own reproduction

The reassessment's material findings (F01/F02/F03/F04) are independently reproduced or source-proven.
**Week 4 Gate = FAIL** stands. No product code was modified; no `blog_db`/`blog_v2` connection was
attempted (guards refused them).


- F01–F08 are real defects in authorized Week 4 deliverable scope; fixing them is a new
  implementation wave and is **not** covered by the prior "complete Week 4" run without a
  fresh confirmation, because F03 changes challenge verification design and F04 requires
  deterministic business seeds.
- No production DB (`blog_db`/`blog_v2`) was touched during this recheck; all reproduction used
  local scratch DBs or pure functions.
- This recheck did not modify product source.

## Required remediation (before M4 can pass)

P0: F01 (CI test DB config compatible with guards), F02 (CLI async resource lifecycle),
F03 (locate+consume the challenge matching the assertion), F04 (restore R22b business E2E),
F07 (full-chain error sanitization).
P1: F05 (structured cross-layer OCR errors), F06 (bound account throttle state), F08 (align
backfill acceptance or explicitly defer).
Also: backend test isolation (remove the 3 `--deselect`) and doc/status consistency.
