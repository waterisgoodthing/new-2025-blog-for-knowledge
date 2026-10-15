# W4-00 — Locked Decisions (executable + plan deltas)

Status: `PASS` (preflight)
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public` (dirty worktree preserved; no source deleted/migrated)

This file records the Week 4 decisions and the **main-agent execution-time deltas**
(`W4-E*`) required because the locked plan text (`tasks/*.md`) did not match current source.
Current source, tests, and runtime evidence outrank the plan text (AGENTS.md §1).

---

## 1. Locked plan decisions (W4-D01 … W4-D07)

| ID | Decision | State |
|---|---|---|
| W4-D01 | Serial order: W4-00 → PR-14 → PR-15 → PR-19 ‖ PR-16 → PR-17 → PR-18 → Gate | LOCKED |
| W4-D02 | OCR diagnostic priority: taxonomy + baseline + UI, no pipeline rewrite | LOCKED |
| W4-D03 | WebAuthn challenge table schema: purpose + binding keys + TTL | LOCKED |
| W4-D04 | Throttling: dual-dimension (account+IP), graduated delays, no lockout | LOCKED |
| W4-D05 | Polish transient (exempt); persisted AI must link target_id | LOCKED |
| W4-D06 | CI four jobs (frontend / backend / runtime smoke / E2E workers=1) | LOCKED |
| W4-D07 | Legacy cleanup: three-part evidence (grep + test + runtime) required | LOCKED |

---

## 2. Execution-time deltas (W4-E*) — main agent, evidence-backed

### W4-E01 — PR-14 must NOT add a migration/column
- Verified: no `capture_recognition_service.py`, no `CaptureRecognition` model. Real path is
  `services/capture_recognition.py:recognize_image` → `services/ai_gateway.call_vision` →
  `CaptureItem` (table `capture_items`), which already stores `error_code String(50)` and
  `error_message_safe String(300)`.
- Decision: implement the taxonomy as a **mapping over the existing `error_code` vocabulary**
  (`AiErrorCode` + capture-specific codes) and expose a **derived** `failure_category` in
  `CaptureOut` (computed, not persisted). No new column, no migration.
- Rationale: the Week 4 gate requires a single migration head at **033** (reserved for PR-15);
  PR-14 adding 033/034 would violate the gate matrix and exceeds the "diagnose, don't rewrite" scope.

### W4-E02 — OCR 10-sample baseline: local harness, real-provider rate NOT_VERIFIED
- Verified: the only real outbound call is `ai_service._call_provider` (external provider);
  no provider credentials are configured in this environment and external writes are out of the
  authorized local-only scope.
- Decision: run the 10-sample baseline through the **deterministic local recognition path** (the
  existing fake adapter + taxonomy harness) with 10 diverse synthetic samples, and classify each
  outcome. The **real-provider success rate is `NOT_VERIFIED`**.
- Entry-point decision: do **not** disable/label the Capture entry on unverified data (an
  unproven product change would be scope creep). Gate records OCR baseline as `PARTIAL`
  (taxonomy + UI verified; real success rate unverified) with honest disclosure.

### W4-E03 — PR-15 DB-backed challenges: signature + semantics
- Verified real globals: `_reg_challenge_store`, `_auth_challenge_store`,
  `_operator_reg_challenge_store`; registration/auth use fixed `"current"`, operator uses an
  ephemeral random `session_id` (from `auth.py:338`), operator pop-before-verify.
- Decision: challenge functions gain an explicit `db` session parameter; call sites
  (`auth.py`, `cli.py`) updated. Table binding: registration/authentication unbound
  (`session_id`/`user_id` NULL, select latest unconsumed by `purpose`); operator bound by
  `session_id`. TTL default 300s (configurable). Preserve per-ceremony consume semantics:
  reg/auth consume **on success**, operator consume **on attempt**.
- Rationale: the plan's `user_id=current_user.id` binding is impossible — authentication options
  are generated publicly without a user, and registration is CLI-only.

### W4-E04 — PR-16 account key = `username`
- Verified: `LoginRequest` is `{username, password}`; there is no email field and no existing
  throttle config. Decision: account dimension keys on `username`.

### W4-E05 — PR-19 must add the wiring
- Verified: `ai_runs.target_type`/`target_id` exist (String(50)/String(100), nullable) but the
  only gateway insert path (`ai_gateway._start_run_record`) passes neither → always NULL today.
- Decision: thread `target_type`/`target_id` from `call_vision`/`call_text` through
  `_start_run_record`; Capture recognition passes `target_type='Capture'`, `target_id=<capture id>`.
  Polish remains exempt (no target linkage). Creation-type backfill remains NULL-valid, documented.

### W4-E06 — PR-17 CI is locally reproduced only
- Remote push is NOT_AUTHORIZED. Jobs are validated by local reproduction; "CI green on remote"
  and "intentional-break caught by CI" are `NOT_VERIFIED` (not falsified).

### W4-E07 — PR-18 deletion set is much smaller than planned
- Verified SAFE_TO_DELETE (zero call sites, no tests, not routed):
  `src/components/wip.tsx`, `src/app/manage/components/manage-placeholder-page.tsx`,
  `src/app/manage/(workspace)/components/future-capability-page.tsx`, `src/app/music/list.ts`,
  and the dead `readFileAsText` import in `src/app/blog/page.tsx`.
- Verified IN_USE (not deleted): `services/sm2.py` (registered `/api/review` router imports it),
  legacy `src/lib/api/review.ts`, all 4 dashboard test files (22/22 pass, zero skipped),
  legacy weak-point analytics, `knowledge_assistant`, `review_planner`, canonical KP analytics.
- The plan's "broken Dashboard quick-action tests" **do not exist** and "duplicate analytics"
  were not replaced by PR-10. Net line reduction will be far below the plan's ≥500 secondary metric.

---

## 2b. Amendment W4-E08 — WebAuthn raw challenge column retained (supersedes the D03 "hash-only" wording)

- Independent review of PR-15 (F2, HIGH) flagged that migration 033 stores a raw
  `challenge` column, while W4-D03 / PR-15 acceptance text says "不存明文 challenge" / "Challenge hash
  prevents plaintext challenge storage".
- Main-agent decision: **retain the raw `challenge` column (b64url) alongside `challenge_hash`
  (sha256)**. Rationale: `webauthn.verify_registration_response` / `verify_authentication_response`
  require the **server-side raw challenge** as `expected_challenge`. A hash-only table cannot feed
  the library without either (a) reconstructing the challenge from the client's `clientDataJSON`
  and comparing hashes manually (replacing the library's challenge check with custom parsing — higher
  risk), or (b) passing the client-supplied challenge as expected (circular, unsafe).
- Residual exposure: a random 32-byte, single-use, TTL-bounded (default 300s) nonce exists in the DB
  in plaintext for ≤ TTL. It is not a credential or long-lived secret; the raw challenge is never
  logged (verified). This supersedes the "hash-only" wording of W4-D03 / PR-15 acceptance.
- `challenge_hash` is retained for integrity/audit and lookup support.

---

## 3. Evidence integrity

- Baseline: `w4-00-baseline-status.txt`, `w4-00-baseline-diffstat.txt`, `w4-00-baseline.diff`.
- Migration head: `w4-00-migration-head.txt` → single head **032**.
- Inventories: `w4-00-ocr-inventory.md`, `w4-00-webauthn-inventory.md`, `w4-00-cleanup-candidates.md`.
- Scratch guard: `scripts/week4-scratch-guard.py` (37 tests OK) + extended
  `backend/app/utils/scratch_db_safety.py` allowlist to `astra_week[34]_*` (additive; still
  rejects `blog_db`/`blog_v2`/remote hosts). Verified `.env` `blog_v2` refused (exit 1).
