PR-19 — AI Call Site Audit
==========================

Scope: every production call into the AI gateway plus the one AI path that
bypasses it. Classification follows docs/architecture/ai-governance.md.

Legend
- LINKED (persisted): call passes target_type/target_id; the run points at the
  durable entity it operates on.
- NOT_YET_LINKED (gap): call goes through the gateway and creates an AiRun, but
  the call site does not pass a target today (target_id = NULL). Every such
  persisted-canonical caller is listed explicitly so none is silently
  unclassified; these are known coverage gaps (out of PR-19 scope), not exempt.
- EXEMPT (transient): output is streamed to the user and not persisted; no
  durable entity exists to link, and no AiRun is created.

Gateway entry point
-------------------
`ai_gateway._start_run_record` is the only production caller of
`ai_run_service.start_ai_run`. After PR-19 it accepts optional
`target_type`/`target_id` and forwards them; `call_text`, `call_vision`,
`call_general`, `call_stream` all expose the same optional kwargs.
`_finish_run_record` is unchanged; `retry_ai_run` already copies the parent's
target.

Audit
-----

| # | File:line | Entry | Task type(s) | Classification |
| --- | --- | --- | --- | --- |
| 1 | backend/app/services/capture_recognition.py:89 | `call_vision` | capture_recognition | LINKED — Capture (`target_type="Capture"`, `target_id=<capture_id>`); only when `capture_id` is not None |
| 2 | backend/app/services/capture_ai_draft.py:92 | `call_text` | capture_draft | LINKED — Capture (`target_type="Capture"`, `target_id=<capture_id>`); only when `capture_id` is not None. `capture_service.trigger_draft` now passes `capture_id=str(capture.id)` |
| 3 | backend/app/routers/ai_polish.py:17 (`polish` → `polish_stream`) | direct `httpx` streaming (no gateway) | n/a | EXEMPT — transient preview, never persisted, no AiRun created |
| 4 | backend/app/services/recommendation.py:90 | `call_general` | recommendation | NOT_YET_LINKED (gap) |
| 5 | backend/app/services/mistake_staged_service.py:28 | `call_vision` | mistake_question_draft | NOT_YET_LINKED (gap) |
| 6 | backend/app/services/mistake_staged_service.py:35 | `call_text` | mistake_question_draft | NOT_YET_LINKED (gap) |
| 7 | backend/app/services/mistake_staged_service.py:91 | `call_text` | mistake_error_interpretation | NOT_YET_LINKED (gap) |
| 8 | backend/app/services/mistake_staged_service.py:128 | `call_text` | mistake_final_analysis | NOT_YET_LINKED (gap) |
| 9 | backend/app/services/netease_service.py:253 | `call_text` | netease_reason | NOT_YET_LINKED (gap) |
| 10 | backend/app/services/diagram_service.py:67 | `call_text` | diagram_structured | NOT_YET_LINKED (gap; classify as persisted-linked or transient when wired) |
| 11 | backend/app/services/diagram_service.py:152 | `call_text` | diagram_fallback | NOT_YET_LINKED (gap; classify as persisted-linked or transient when wired) |
| 12 | backend/app/routers/ai.py:116 | `call_vision` | analyze_mistake | NOT_YET_LINKED (gap) |
| 13 | backend/app/routers/ai.py:150 | `call_text` | analyze_text | NOT_YET_LINKED (gap) |
| 14 | backend/app/routers/ai.py:259 | `call_text` | generate_variant | NOT_YET_LINKED (gap) |
| 15 | backend/app/routers/ai.py:301 | `call_text` | generate_knowledge_card | NOT_YET_LINKED (gap) |
| 16 | backend/app/routers/ai.py:342 | `call_text` | knowledge_summary | NOT_YET_LINKED (gap) |
| 17 | backend/app/routers/ai.py:395 | `call_text` | prompt_test | NOT_YET_LINKED (gap; admin diagnostic) |
| 18 | backend/app/routers/ai.py:397 | `call_vision` | prompt_test | NOT_YET_LINKED (gap; admin diagnostic) |

Gap summary: 15 unlinked gateway call sites (rows 4-18), all enumerated above.
Every gateway caller is now either LINKED (rows 1-2), EXEMPT (row 3), or an
explicit NOT_YET_LINKED gap — none is silently unclassified.

Notes
-----
- Rows 1 and 2 are the PR-19 deliverables: Capture recognition and Capture
  draft AiRuns are now traceable to their Capture row.
- Capture draft links to `target_type='Capture'`, not to MistakeDraft/Question:
  the AI acts on the capture's recognized text and stores its suggestion on the
  capture row, which may never be converted. The downstream draft is created
  later by `capture_service.convert_capture` from human-confirmed data, so the
  run is intentionally not relinked.
- Polish is exempt because it bypasses the gateway entirely and streams a
  transient preview that is never auto-persisted; adding linkage would require
  making the preview durable, at which point the classification must be revised.
- "NOT_YET_LINKED" rows are known coverage gaps (out of the PR-19 write scope);
  they are not exempt and should be classified per the transient/persisted rule
  when they are addressed.
- Creation-type backfill: `ai_run_service.backfill_ai_run_target` exists and is
  unit-tested, but no production confirmation endpoint calls it yet
  (NOT_YET_WIRED; see docs/architecture/ai-governance.md).
