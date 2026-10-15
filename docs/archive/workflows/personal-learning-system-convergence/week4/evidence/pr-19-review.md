# PR-19 Independent Review — AI Governance (Run target linkage)

Reviewer: independent (did not implement PR-19).
Mode: READ-ONLY. No source modified. Only this evidence file created. No git write.
Scope: `backend/app/services/ai_gateway.py`, `capture_recognition.py`,
`capture_ai_draft.py`, `capture_service.py`, `backend/app/routers/ai_polish.py`,
`backend/tests/test_ai_governance.py`, `docs/architecture/ai-governance.md`,
`evidence/pr-19-*`.

## Verdict

**PASS_WITH_NOTES**

The core PR-19 deliverable is correct: `target_type`/`target_id` are threaded
through all four gateway entry points, persisted on `ai_runs`, and the two
Capture call sites link to their Capture row. The polish exemption is accurate.
The targeted test run passes (32 passed).

One HIGH accuracy defect prevents a clean PASS: the documentation and the new
test present a "confirmation backfill" of `ai_runs.target_id` as implemented and
verified, but no code performs that backfill and the test is tautological. The
PR must not claim the backfill acceptance criterion as met until this is
corrected. There is no runtime/data breakage, so this is a note with required
corrections, not a code failure.

Severity counts: **BLOCKER 0, HIGH 1, MEDIUM 1, LOW 2, INFO 3.**

## Findings

| id | severity | problem | evidence (file:line) | required action |
| --- | --- | --- | --- | --- |
| F1 | HIGH | Doc and test claim an implemented/verified creation-type backfill of `ai_runs.target_id` ("the owning service backfills target_id … on user confirmation/save"). No code updates an existing `AiRun.target_id`; the only writes are at creation (`start_ai_run`) and retry. The new test named `test_confirmation_backfills_target_id` manually assigns ORM attributes in-session and reads them back — it invokes no confirmation service/endpoint, so it asserts SQLAlchemy attribute round-tripping, not backfill behavior. `evidence/pr-19-tests.txt` lists it as a passing "confirmation backfills target_id" scenario. | `docs/architecture/ai-governance.md:42-43`, `:64-75`; `backend/tests/test_ai_governance.py:197-208`; `evidence/pr-19-tests.txt:71-72`; `backend/app/services/ai_run_service.py:92-109` (only creation write), `:164-174` (retry copy); no `.target_id =` on `AiRun` anywhere (`rg` over `backend/app` returns only DraftItem/MistakeDraft backfills at `draft_service.py:337-340`, `mistake_service.py:169`) | Reword `ai-governance.md` to state the backfill contract is **defined but not yet exercised/implemented** (no creation-type flow is wired). Rename/remove/rescope `test_confirmation_backfills_target_id`, or replace it with a real service-level test once a confirmation→backfill implementation exists. Correct `pr-19-tests.txt` so it does not present this as verified backfill. Reproduction: `rg -n "\.target_id\s*=" backend/app` shows no `AiRun` assignment outside `start_ai_run`; the test body only sets `run.target_type`/`run.target_id` directly. |
| F2 | MEDIUM | "Retry copies the parent's target" is asserted only by code inspection, not by any test. The existing retry test checks parent/attempt/replay_input but not `target_type`/`target_id`. | `backend/app/services/ai_run_service.py:167-168`; `backend/tests/test_ai_run_service.py:107-131` (no target assertion) | Add `target_type`/`target_id` to the parent in `test_retry_creates_child_without_changing_parent` and assert the child copies them. |
| F3 | LOW | The query evidence claims the `test_recognition_failure_zero_pollution` run provides an end-to-end observation that `capture_service` passes `capture_id`; that test asserts zero pollution only and contains no `AiRun` linkage assertion. The linked coverage row in the query came from a manually seeded run, not from the test. | `evidence/pr-19-airun-query.txt:41-46`; `backend/tests/test_capture_service.py:201-215` | Either add an explicit `AiRun` linkage assertion to a capture-service test, or reword the evidence to separate "seeded row" from "test-derived" observations. |
| F4 | LOW | The two "no target" tests patch out `_start_run_record` and assert only the forwarded kwargs. They verify call shape, not that NULL actually persists to a row (the "NULL is a valid terminal state" contract). | `backend/tests/test_ai_governance.py:102-131`, `:165-193` | Acceptable as forwarding tests; note the scope, or add one un-mocked case asserting a persisted NULL row for a creation-time call. |
| F5 | INFO | Evidence files live at repo-root `evidence/pr-19-*` (matching the task's own "Evidence Location"), not at `docs/workflows/.../week4/evidence/pr-19-*` as referenced in the review request. | `evidence/pr-19-ai-call-audit.md`, `evidence/pr-19-tests.txt`, `evidence/pr-19-airun-query.txt`; task lists `docs/.../tasks/pr-19.md:176-182` | Clarify the canonical evidence location; no code change. |
| F6 | INFO | Capture draft is linked to `Capture`, whereas the task suggested the produced `MistakeDraft`/`Question` UUID. Linking to `Capture` is defensible (the draft output is stored on the Capture row) and is documented, but the divergence from the task's suggested target is not called out as a decision. | `docs/architecture/ai-governance.md:52`; `backend/app/services/capture_ai_draft.py:92-98`; task `docs/.../tasks/pr-19.md:63-66` | Add one sentence to the doc explaining why `Capture` (not `MistakeDraft`) is the correct target for the draft run. |
| F7 | INFO | `routers/ai.py` sites, `mistake_staged_service`, `diagram_service`, `recommendation`, `netease_reason` are all marked "Not yet linked" (documented gap, not silent). The doc does not distinguish which of these actually produce/persist canonical entities (they may instead be "persisted target-linked" and simply missing linkage, or transient). | `docs/architecture/ai-governance.md:54-62`; `evidence/pr-19-ai-call-audit.md:27-46` | Follow-up: per-site classification (persisted vs transient) so the coverage gap is prioritized accurately. Not a PR-19 blocker; all 17 gateway sites are enumerated. |

## Confirmations (verified against source)

- **Threading (req 1).** `_start_run_record` accepts `target_type`/`target_id` and forwards them to `ai_run_service.start_ai_run` (`ai_gateway.py:104-138`). `call_text`/`call_vision`/`call_general`/`call_stream` all expose the kwargs and forward them (`ai_gateway.py:270-284`, `:316-330`, `:361-375`, `:408-427`). `start_ai_run` stores them on the `AiRun` model (`ai_run_service.py:92-106`; model columns `ai_run.py:20-21`).
- **No incorrect caller.** Only two call sites pass target kwargs: `capture_recognition.py:89-94` and `capture_ai_draft.py:92-98`. Both use `target_type="Capture" if capture_id is not None else None` with `target_id=capture_id` — correct pairing. No other production caller passes these kwargs.
- **Retry copies parent target (req 1).** `retry_ai_run` passes `target_type=parent.target_type, target_id=parent.target_id` (`ai_run_service.py:164-174`, esp. `:167-168`). Correct by inspection (see F2 for missing test).
- **Capture recognition + draft (req 2).** `recognize_image` links `Capture` (`capture_recognition.py:92-93`); `draft_mistake` links `Capture` (`capture_ai_draft.py:96-97`). `capture_service.trigger_recognition` passes `capture_id=str(capture.id)` (`capture_service.py:212-218`) and `capture_service.trigger_draft` now passes it too (`capture_service.py:285`) — this resolves the earlier INFO noted in the task.
- **Unlinked-but-documented (req 2).** `_start_run_record` is the only production caller of `start_ai_run` (besides retry). All remaining gateway call sites are enumerated and marked as known gaps in `ai-governance.md:54-62` and `pr-19-ai-call-audit.md` — documented, not silently ignored.
- **Polish exemption (req 3).** `polish` bypasses the gateway and streams via direct `httpx` (`ai_polish.py:17-18`, `ai_polish_service.py:32,67,121-125`), never persists to a durable entity, and creates no `AiRun`. The doc states this correctly (`ai-governance.md:53`, `:28-33`). The "creation-type NULL→backfill contract" wording is the overclaim covered by F1.
- **Tests are provider-mocked / no network (req 4).** The governance tests patch `ai_gateway._call_with_fallback` (`test_ai_governance.py:81-87`, `:144-151`) and `_write_call_log`; the polish test patches `ai_polish_service._get_stream_providers` to `[]` (`:225`), exercising the real "no provider" branch. The `test_confirmation_backfills_target_id` test is the one exception in meaningfulness (F1): it asserts behavior the code does not implement.

## Raw command output (req 5)

Command:

```
python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr19" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_ai_governance.py tests/test_ai_gateway.py tests/test_capture_service.py -q"
```

Output (verbatim):

```
................................                                         [100%]
=============================== warnings summary ===============================
tests/test_ai_gateway.py::LogWriteFailureTest::test_log_write_failure_does_not_block
  /Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py:98: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
  Coroutine created at (most recent call last)
    File "/opt/homebrew/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/runners.py", line 118, in run
      return self._loop.run_until_complete(task)
    ...
    File "/Users/limengyang/2025-blog-public/backend/tests/test_ai_gateway.py", line 336, in test_log_write_failure_does_not_block
      gw = await call_text("test_task", [{"role": "user", "content": "hi"}])
    File "/Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py", line 305, in call_text
      await _write_call_log(task_type_str, gw_result, input_summary, prompt_version=prompt_version)
    File "/Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py", line 98, in _write_call_log
      session.add(log)
    ...
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_ai_gateway.py::LogWriteFailureTest::test_write_call_log_catches_exception
  /Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py:98: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
  Coroutine created at (most recent call last)
    File "/opt/homebrew/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/async_case.py", line 113, in _callMaybeAsync
      return self._asyncioRunner.run(
    ...
    File "/Users/limengyang/2025-blog-public/backend/tests/test_ai_gateway.py", line 361, in test_write_call_log_catches_exception
      await _write_call_log("test", result, "summary")
    File "/Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py", line 98, in _write_call_log
      session.add(log)
    ...
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
32 passed, 2 warnings in 2.13s
PASS: db_name='astra_week4_pr19' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_ai_governance.py tests/test_ai_gateway.py tests/test_capture_service.py -q']
```

Result: **PASS — 32 passed, 2 warnings in 2.13s** against `astra_week4_pr19`. Exit status 0; scratch-guard reported the expected `db_name='astra_week4_pr19'`. The 2 warnings are pre-existing in `test_ai_gateway.py` (AsyncMock session handling), unrelated to PR-19, and occur in tests this PR did not modify. No DB was created or dropped. This reproduces the evidence claim in `evidence/pr-19-tests.txt:33` exactly.

## Unresolved questions

1. Is there any actual creation-type AI flow currently in scope that must backfill `ai_runs.target_id`, or is the backfill contract purely prospective? The doc reads as if a flow implements it; source shows none does.
2. For capture draft, is the intended canonical target `Capture` (implemented and documented) or the resulting `MistakeDraft`/`Question` (as the task's acceptance text suggests)? Needs an explicit decision.
3. Do `generate_variant`, `generate_knowledge_card`, and `knowledge_summary` persist canonical entities? If yes, they may belong under "persisted target-linked (missing linkage)" rather than the generic "not yet linked" bucket.
4. Where is canonical PR-19 evidence expected to live — repo-root `evidence/` (where it is) or the week4 `evidence/` directory referenced by the review request?

---

# §Recheck (rework verification)

Re-verified against current source. Reviewer unchanged (independent, read-only).
**Final verdict: PASS.** All prior findings CLOSED. Severity counts now:
BLOCKER 0 · HIGH 0 · MEDIUM 0 · LOW 0 · INFO 0 (3 original INFO reclassified as
closed/resolved).

## Per-finding status

| id | prior severity | status | recheck evidence |
| --- | --- | --- | --- |
| F1 | HIGH | **CLOSED** | `backfill_ai_run_target` implemented at `backend/app/services/ai_run_service.py:178-203`: it loads the run via `db.get`, returns `False` if missing, sets `target_id` (and `target_type` only when provided), `await db.flush()`, returns `True`; caller owns commit (documented). The tautological test is gone. `test_backfill_helper_links_existing_run` (`backend/tests/test_ai_governance.py:244-263`) creates a **real committed AiRun with NULL target through the gateway** (`_create_gateway_null_run` → `call_text`, `:212-242`), then calls the real helper in a fresh session + `commit()`, then **re-reads the row from a new session** via `_fetch_by_id` and asserts `target_type="Mistake"` / `target_id=<id>`. Not a manual ORM assignment. `test_backfill_helper_returns_false_for_missing_run` (`:265-273`) covers the not-found path; `test_abandoned_suggestion_keeps_null_without_error` (`:275-282`) reads a real gateway-created row and asserts NULL persists. Doc no longer overclaims: `docs/architecture/ai-governance.md:42-51` and `:96-98` state **NOT_YET_WIRED** and "This section is prospective, not a description of current runtime behavior." Grep confirms no production caller: `rg -n "backfill_ai_run_target" backend/app` returns only the definition at `ai_run_service.py:178`; all call sites are tests; `rg` over `backend/app/routers` returns none. Wording matches reality. |
| F2 | MEDIUM | **CLOSED** | `RetryTargetPropagationTest::test_retry_copies_parent_target` added (`backend/tests/test_ai_governance.py:285-302`); it seeds a parent with `target_type="Capture"` + `target_id`, calls `retry_ai_run`, and asserts `retry.target_type=="Capture"`, `retry.target_id==self.target_id`, plus parent/attempt. |
| F3 | LOW | **CLOSED** | The misleading "test_recognition_failure_zero_pollution confirms capture_id" claim is removed. `docs/workflows/.../week4/evidence/pr-19-airun-query.txt` now shows a guard-routed seed → coverage-before → helper call → coverage-after sequence with before/after SQL (linked_runs 1/3 → 2/3), and the abandoned run stays NULL. No test-derived claim is conflated with seeded rows. |
| F4 | LOW | **CLOSED** | The persisted-NULL contract is now demonstrated by a real committed gateway row (abandoned test, `:275-282`) rather than only kwarg-shape assertions. The two "without target" forwarding tests (`:117-146`, `:180-208`) remain shape-only, which is acceptable now that the NULL-persistence path is covered elsewhere. |
| F5 | INFO | **CLOSED** | Evidence moved: root `evidence/` is now empty; `pr-19-ai-call-audit.md`, `pr-19-airun-query.txt`, `pr-19-tests.txt` live under `docs/workflows/personal-learning-system-convergence/week4/evidence/`. (Original review's unresolved Q4 resolved.) |
| F6 | INFO | **CLOSED** | Dedicated rationale added: `docs/architecture/ai-governance.md:72-80` "Why Capture draft links to `Capture`, not to `MistakeDraft`/`Question`", mirrored in `pr-19-ai-call-audit.md:58-62`. |
| F7 | INFO | **CLOSED** | All 15 unlinked gateway sites (rows 4-18) relabeled `NOT_YET_LINKED (gap)` with an explicit gap summary (`pr-19-ai-call-audit.md:10-13,34-52`); `ai-governance.md:66-70` states every gateway caller is linked, exempt, or listed. No site silently unclassified. |

## Raw recheck command output (req 4)

Command:

```
python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr19" -- bash -c "cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_ai_governance.py tests/test_ai_gateway.py tests/test_capture_service.py -q"
```

Output (verbatim, tracebacks elided only where marked `...`):

```
..................................                                       [100%]
=============================== warnings summary ===============================
tests/test_ai_gateway.py::LogWriteFailureTest::test_log_write_failure_does_not_block
  /Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py:98: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
  ...
tests/test_ai_gateway.py::LogWriteFailureTest::test_write_call_log_catches_exception
  /Users/limengyang/2025-blog-public/backend/app/services/ai_gateway.py:98: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
  ...
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
34 passed, 2 warnings in 2.26s
PASS: db_name='astra_week4_pr19' source=explicit:--url; executing ['bash', '-c', 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_ai_governance.py tests/test_ai_gateway.py tests/test_capture_service.py -q']
```

Result: **PASS — 34 passed, 2 warnings in 2.26s**, exit 0, on `astra_week4_pr19`.
This matches the implementer's claim and `pr-19-tests.txt` (34 passed). The 2
warnings are the same pre-existing AsyncMock warnings in untouched
`test_ai_gateway.py`; unrelated to PR-19. No DB created or dropped.

## Residual risk (post-rework)

1. **Backfill integration is prospective (documented).** `backfill_ai_run_target`
   has no production caller and there is no confirmation endpoint wired. If a
   future creation-type flow ships without calling it, `target_id` silently
   stays NULL. This is now correctly documented as NOT_YET_WIRED, not a defect,
   but there is no guardrail that would surface a missed wiring.
2. **Helper commits nothing.** The helper `flush`es only; a caller that forgets
   to `commit` (or rolls back) loses the linkage. This is documented ("caller
   owns the surrounding transaction") but is a foot-gun with no test asserting
   the no-commit case is caller responsibility.
3. **`target_id` remains an unvalidated string with no FK** to the target
   entity; a wrong/arbitrary id can be persisted. Pre-existing design, outside
   PR-19 scope.
4. **15 unlinked gateway call sites remain** (documented gaps). The audit
   enumerates them but does not yet classify each as persisted-canonical vs
   transient; prioritization of closure is a follow-up.
5. **Two forwarding-only tests** (`test_call_without_target_records_null_target`,
   `test_recognize_image_without_capture_id_has_no_target`) still patch out
   `_start_run_record`, so they validate call shape rather than persistence.
   Mitigated by the real persisted-NULL abandoned-run test.
6. No data-integrity or auth/schema risk introduced by PR-19; all changes are
   nullable-column linkage, a new helper, tests, and docs. No migration added.
