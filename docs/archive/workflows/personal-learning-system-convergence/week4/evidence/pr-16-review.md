# PR-16 — Independent Review: Login Throttling

- Reviewer role: independent (did not implement PR-16)
- Date: 2026-09-26
- Scope: `backend/app/config.py`, `backend/app/services/login_throttle.py`,
  `backend/app/routers/auth.py` (login), `backend/tests/test_login_throttling.py`,
  `backend/tests/test_login_throttling_integration.py`
- Mode: READ-ONLY (no source modified; no DB created/dropped; no git write)
- Scratch target: `postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr16`
  (run through `scripts/week4-scratch-guard.py`)

## Verdict

**PASS_WITH_NOTES**

The graduated delay schedule, delay placement, credential-safety, dual-dimension
behavior, account reset, disabled flag, and config externalization all match the
acceptance criteria. One MEDIUM correctness defect exists in the IP TTL decay
(write path revives expired counters; entries are never evicted; the module
docstring claims otherwise). No BLOCKER or HIGH findings. F1 below has a
reproduction.

## Findings

| id | severity | problem | evidence (file:line) | required action |
|---|---|---|---|---|
| F1 | MEDIUM | IP TTL decay is read-only. `_live_failures` treats an expired entry as absent but never deletes it, and `record_failure` increments the stale counter without a TTL check. A single failure AFTER the TTL elapsed revives the old count (3 prior + 1 = 4) and applies a 5s delay instead of restarting at 0/0s. `_ips` therefore also grows without bound. This contradicts "IP counter expires after TTL" and the docstring "lazily dropped when read". | `login_throttle.py:58` (`record_failure`, no TTL check), `login_throttle.py:86-91` (`_live_failures` returns 0 but no delete), `login_throttle.py:14-19` (inaccurate docstring) | Drop/skip the entry on read when expired, or reset the counter in `record_failure` when `now - updated_at > ttl`; correct the docstring. Add a unit test for "failure after TTL expiry starts a fresh count". |
| F2 | LOW | PR-16 acceptance "Evidence" artifacts are absent. No `pr-16-unit-tests.txt`, `pr-16-integration-timing.txt`, or `pr-16-manual-test.md` exist under the week4 evidence dir, and `TRACKING.md` still lists PR-16 items as `NOT_STARTED`. | `docs/.../week4/evidence/` (only `pr-14-*`, `pr-15-*`, `w4-00-*` present); `TRACKING.md:116-124`, `TRACKING.md:190-191` | Produce the named evidence files (this review records the raw run) and update `TRACKING.md` status. |
| F3 | LOW | Timing-test flakiness risk. `test_successful_login_resets_account_delay` asserts `elapsed < 0.4` for one default-cost bcrypt verify (cost=12); measured 0.165-0.168s here, but cost-12 verify commonly reaches 0.3-0.5s on slower CI. The 2s test's upper bound 2.5s leaves only 0.5s headroom over a guaranteed 2s sleep. | `test_login_throttling_integration.py:213-216` (0.4 bound), `test_login_throttling_integration.py:29-30,107-113` (1.5-2.5 window) | Widen the reset-test bound or monkeypatch bcrypt cost; keep/relax the 2s window deliberately. |
| F4 | INFO | Throttled WARN line logs `account` (username), `ip`, and `count`; no password/token is logged. This matches the PR-16 pseudocode, but is broader than "count only". | `auth.py:188-194`; `auth.py:204-210` | None required; confirm username-in-log fits the project's logging policy. |
| F5 | INFO | `LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES` alert is emitted using `get_failure_count` = `max(account, ip)`, so an IP-only spike is logged under the account label. | `auth.py:202-210`, `login_throttle.py:128-135` | Optional: label the alert with the dimension that crossed the threshold. |

Severity counts: **BLOCKER 0 · HIGH 0 · MEDIUM 1 · LOW 2 · INFO 2**.

## Verification Detail (against acceptance)

1. **Schedule (attempt-index) — PASS.** Router computes the delay from
   previously recorded failures and sleeps before auth. Simulated/pre-attempt
   sequence is `0, 0, 0, 2, 5, 15, 15, 15` for attempts 1-8, i.e. attempts 1-3
   → 0s, 4th → 2s, 5th → 5s, 6th+ → 15s (capped). The implementer's
   `failures >= threshold` bound (`login_throttle.py:98-103`) corrects the
   off-by-one in the PR-16 pseudocode and matches acceptance, not the
   pseudocode. Asserted by `test_login_throttling.py:51-61` and measured
   end-to-end (4th attempt elapsed 2.006s).
2. **Delay placement / credential safety — PASS.** Delay at `auth.py:184-195`
   precedes the DB query (`:197`), `verify_password` (`:199`), and session work.
   401 detail unchanged: `"Invalid credentials"` (`auth.py:211`). No
   password/token in any log line; throttled path logs at WARN.
3. **Reset / decay / dual dimension / disable — PASS (with F1).** Account reset
   on success (`auth.py:213-214`, `login_throttle.py:78-83`). Dual dimension via
   `max()` (`login_throttle.py:122-125`); account persists across IPs and IP
   triggers for a fresh account, both verified by integration tests.
   `LOGIN_THROTTLE_ENABLED=False` gates both the delay and `record_failure`
   (`auth.py:184,200,213`; `login_throttle.py:108-109`). IP TTL decay is
   correct on the read path only — see F1 for the write path.
4. **Config externalizable — PASS.** All five settings exist with sensible
   defaults (`config.py:61-65`); `parse_login_throttle_delays` ignores blank,
   non-numeric, and negative tokens and handles `None` (`config.py:6-25`); no
   hardcoded delay, threshold, or TTL values in the service logic (all read from
   settings).
5. **Tests — PASS (with F3).** Not tautological: unit tests drive the real
   service + real parser; integration tests hit the real `POST /api/auth/login`
   endpoint, and the 2s case measures genuine wall-clock elapsed time. Flakiness
   noted in F3.
6. **Command run — PASS, 19 passed** (raw output below).

## Reproduction of F1 (READ-ONLY, no DB, no source change)

`backend/.venv/bin/python` snippet monkeypatching `login_throttle._now`:

```
immediately after 3 fails: delay= 2.0 count= 3
after TTL expiry (read): delay= 0.0 count= 0
after ONE new failure post-TTL: delay= 5.0 count= 4   <-- expected 0.0 / 1
ips dict still holds entry: ['1.1.1.1']
```

bcrypt cost tag = 12; verify samples = `[0.168, 0.165, 0.165]` s.

## Raw command output

Guard validation:

```
$ python3 scripts/week4-scratch-guard.py check --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr16"
PASS: db_name='astra_week4_pr16' source=explicit:--url
```

Exact required run:

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr16" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_login_throttling.py tests/test_login_throttling_integration.py tests/test_auth_error_handling.py -q"
...................                                                      [100%]
19 passed in 4.79s
PASS: db_name='astra_week4_pr16' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_login_throttling.py tests/test_login_throttling_integration.py tests/test_auth_error_handling.py -q']
```

Verbose run with timing prints (`-v -s`, cache disabled):

```
tests/test_login_throttling.py::test_parse_delays_returns_floats_in_order PASSED
tests/test_login_throttling.py::test_parse_delays_ignores_blank_invalid_and_negative PASSED
tests/test_login_throttling.py::test_delay_schedule_graduated_and_capped PASSED
tests/test_login_throttling.py::test_no_failures_means_no_delay PASSED
tests/test_login_throttling.py::test_account_counter_resets_on_success PASSED
tests/test_login_throttling.py::test_ip_counter_decays_after_ttl PASSED
tests/test_login_throttling.py::test_disabled_throttle_never_delays PASSED
tests/test_login_throttling.py::test_account_dimension_persists_across_ips PASSED
tests/test_login_throttling.py::test_ip_dimension_triggers_for_a_different_account PASSED
tests/test_login_throttling.py::test_failure_count_reports_stricter_dimension PASSED
tests/test_login_throttling.py::test_failure_count_grows_past_alert_threshold PASSED
tests/test_login_throttling_integration.py::test_fourth_failure_has_real_two_second_delay [timing] real default 4th-attempt elapsed=2.006s
PASSED
tests/test_login_throttling_integration.py::test_short_config_fourth_attempt_waits_first_delay [timing] short-config 4th-attempt elapsed=0.254s
PASSED
tests/test_login_throttling_integration.py::test_account_dimension_applies_from_a_new_ip [timing] account-dimension new-IP elapsed=0.255s
PASSED
tests/test_login_throttling_integration.py::test_ip_dimension_applies_to_a_new_account [timing] ip-dimension new-account elapsed=0.255s
PASSED
tests/test_login_throttling_integration.py::test_disabled_throttle_adds_no_delay [timing] disabled-throttle elapsed=0.002s
PASSED
tests/test_login_throttling_integration.py::test_successful_login_resets_account_delay [timing] post-success account reset elapsed=0.167s
PASSED
tests/test_auth_error_handling.py::test_verify_password_treats_disabled_and_malformed_hashes_as_invalid PASSED
tests/test_auth_error_handling.py::test_disabled_account_password_login_returns_401 PASSED
============================== 19 passed in 4.72s ==============================
```

## Unresolved questions

1. F1 fix direction: should the code reset the IP counter on the next
   post-TTL write (restart at 1), or should it evict expired entries eagerly on
   read/write? Both satisfy acceptance; the docstring must match whichever is
   chosen.
2. Is logging the username in throttle WARN/alert lines acceptable under the
   project's privacy/logging policy, or should it be hashed like
   `_set_request_actor`?
3. F2: who owns producing/refreshing the `pr-16-*` evidence artifacts and the
   `TRACKING.md` status flip — implementer or reviewer?

---

# §recheck (2026-09-26)

Re-verified against current source after the implementer's F1/F2/F3 rework.
No source modified by this recheck.

## Recheck verdict

**PASS**

All three actionable findings are CLOSED. The only remaining open item is F5
(INFO, pre-existing, no action required), so the overall verdict improves from
`PASS_WITH_NOTES` to `PASS` for the reviewed scope.

## Per-finding status

| id | severity | status | recheck evidence |
|---|---|---|---|
| F1 | MEDIUM | **CLOSED** | `login_throttle.py` now evicts on read (`_live_count` deletes an expired entry, `:103-105`), sweeps+replaces on write (`record_failure` calls `_evict_expired` then starts a fresh counter, `:126-133`), and `_evict_expired` bounds `_ips` (`:81-87`). No revival path remains. Account non-decay is documented as deliberate (`:20-25`) and asserted by `test_account_counters_do_not_decay_with_ip_ttl`. |
| F2 | LOW | **CLOSED** | `pr-16-unit-tests.txt` (14 passed) and `pr-16-integration-timing.txt` (6 passed) now exist under `docs/.../week4/evidence/`; no root `evidence/pr-16-*`. `TRACKING.md` was **not** re-checked in this pass (still shows `NOT_STARTED` at `TRACKING.md:116-124,190-191` as of last read) — see Remaining. |
| F3 | LOW | **CLOSED** | Reset test bound relaxed to `< 1.0` with schedule `"2,3,4"` (`test_login_throttling_integration.py:192,216-218`), making a broken reset (2s + bcrypt) clearly distinguishable from an unthrottled verify (~0.17s measured). Real 2s test unchanged. |
| F4 | INFO | CLOSED (no action) | Unchanged and still consistent with the PR-16 pseudocode. |
| F5 | INFO | **OPEN** (no action required) | Unchanged; optional dimension labelling of the alert. |

Counts after recheck: **BLOCKER 0 · HIGH 0 · MEDIUM 0 · LOW 0 · INFO 1 open
(F5)**.

## F1 guard assessment (not tautological)

The new tests do guard the exact bug — the pre-fix behavior is asserted against,
not merely described:

- `test_failure_after_ttl_restarts_ip_count` (`test_login_throttling.py:102-114`)
  records 3 failures, advances the frozen clock past TTL, records one more
  failure, then asserts `get_failure_count == 1` and delay `== 0.0`. Before the
  fix this path returned `4` / `5.0` (the revival I reproduced in the first
  review); the comment at `:111` states the pre-fix value explicitly.
- `test_expired_ip_entries_are_evicted` (`:117-129`) seeds 50 distinct IPs,
  advances past TTL, writes one new IP, and asserts `len(lt._ips) == 1`. This
  fails against the old code (map would stay at 51).
- `test_ip_counter_decays_after_ttl` (`:85-99`) now also asserts the read path
  removed the key (`:99`).

Clock control is via `monkeypatch.setattr(lt, "_now", ...)` plus a stubbed
`_ip_ttl_seconds` (`:78-82`), so the TTL tests are deterministic, not
sleep-based.

## Recheck raw output

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr16" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_login_throttling.py tests/test_login_throttling_integration.py tests/test_auth_error_handling.py -q"
......................                                                   [100%]
22 passed in 6.30s
PASS: db_name='astra_week4_pr16' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_login_throttling.py tests/test_login_throttling_integration.py tests/test_auth_error_handling.py -q']
```

Independent F1 reproduction against current source (clock frozen, no DB):

```
after TTL expiry (read): delay= 0.0 count= 0
after ONE new failure post-TTL: delay= 0.0 count= 1     <-- was 5.0 / 4 before fix
ips dict holds: ['1.1.1.1']                              <-- read evicted; write re-added fresh
```

## Remaining

- `TRACKING.md` PR-16 rows still read `NOT_STARTED` (`:116-124`, `:190-191`)
  and were outside this read-only recheck's edit scope; the artifacts now exist,
  so the status flip is the only documentation loose end.
- F5 (INFO) is the sole open finding; no action required unless the account
  alert label is expected to name the failing dimension.
