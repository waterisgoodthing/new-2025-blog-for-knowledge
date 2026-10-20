# Diff Report — SFA-01 Workflow Status Cleanup

## Scope

Inspected workflow status language under:

- `docs/workflows/batch-8-image-mistake-capture`
- `docs/workflows/route-cutover-after-batch-8`
- `docs/workflows/batch-9-ai-gateway-kernel`
- `docs/workflows/batch-10-task-prompt-validator`
- `docs/workflows/batch-10-1-prompt-registry-runtime-integration`
- `docs/workflows/batch-10-2-prompt-engineering-standardization`
- `docs/workflows/batch-11-ai-run-audit-human-review`
- `docs/workflows/stream-run-lifecycle-design-review`
- `docs/workflows/batch-12-ai-provider-routing-cost-stability`

## Conflicting Statuses Found

| Area | Conflict | Resolution |
| --- | --- | --- |
| Batch 8 | README/tasks/checklist/handoff mixed completed P0 items with `待用户验收`, `P0-09 待执行`, and approval-gate language. | Marked P0-01 through P0-09 completed/closed. Kept real AI/OCR as `not verified` and moved it to deferred proof/backlog language. |
| Batch 10.2 | `README.md` and `validation.md` said completed, while `design.md` and `requirements.md` still said `待任务清单审批`. | Updated `design.md` and `requirements.md` to completed/closed. |
| Batch 11 | `README.md` and `tasks.md` said closed, while `design.md` and `requirements.md` still said `待任务清单审批`; handoff retained an earlier RISK-B11-001 blocking section. | Updated `design.md` and `requirements.md`; clarified handoff that RISK-B11-001 was later closed by Browser Fix Patch. |
| Stream B11-003 | README/requirements/risks/tasks/checklist retained design-only or unclosed language while audit/validation documented Stream Endpoint Simplification Patch closure. | Reconciled the folder around the closure path: formal generation moved to non-stream Run chain, legacy stream endpoints deprecated/compatibility-only, complete provider token streaming deferred. |
| Batch 12 | `README.md`, `handoff.md`, and current user context say 12A-D completed; `tasks.md` still used `实施仍待再次批准` for design review items. | Updated status note and repeated P0 design-review item status to `后置实现另列 backlog`; kept database persistence, real probe, events, circuit breaker, temporary disablement, and online editing as deferred items. |

## Files Updated

- `docs/workflows/batch-8-image-mistake-capture/README.md`
- `docs/workflows/batch-8-image-mistake-capture/tasks.md`
- `docs/workflows/batch-8-image-mistake-capture/checklist.md`
- `docs/workflows/batch-8-image-mistake-capture/handoff.md`
- `docs/workflows/batch-10-2-prompt-engineering-standardization/design.md`
- `docs/workflows/batch-10-2-prompt-engineering-standardization/requirements.md`
- `docs/workflows/batch-11-ai-run-audit-human-review/design.md`
- `docs/workflows/batch-11-ai-run-audit-human-review/requirements.md`
- `docs/workflows/batch-11-ai-run-audit-human-review/handoff.md`
- `docs/workflows/stream-run-lifecycle-design-review/README.md`
- `docs/workflows/stream-run-lifecycle-design-review/requirements.md`
- `docs/workflows/stream-run-lifecycle-design-review/risks.md`
- `docs/workflows/stream-run-lifecycle-design-review/tasks.md`
- `docs/workflows/stream-run-lifecycle-design-review/checklist.md`
- `docs/workflows/batch-12-ai-provider-routing-cost-stability/tasks.md`
- `docs/workflows/system-freeze-acceptance-sprint/tasks.md`

## Remaining Deferred Backlog

These are deferred enhancements, not current acceptance blockers unless later evidence proves otherwise:

- Batch 8 true AI/OCR provider proof.
- Complete provider token streaming lifecycle audit, including disconnect and generator exceptions.
- Partial output artifact design.
- ProviderProfile / ModelProfile / RoutingRule database persistence.
- `ai_usage_daily` persistence.
- Actual token usage persistence and cost estimation.
- Budget/quota enforcement.
- Real provider health probe and health event table.
- Automatic circuit breaker, cooldown, and temporary provider disablement.
- Provider/routing/cost/health online editing.
- Prompt admin, A/B testing, hot updates, and Prompt effectiveness evaluation.

## Residual Status Text

The only remaining matches for `待批准` / `未批准` scans are not contradictions:

- `batch-12-ai-provider-routing-cost-stability/audit.md` explicitly lists deferred items not approved for execution.
- `batch-8-image-mistake-capture/validation.md` preserves a historical diff note saying README had once moved from `待批准` to a later status.
