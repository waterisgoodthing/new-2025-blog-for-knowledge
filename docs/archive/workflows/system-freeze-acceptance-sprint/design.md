# Design — System Freeze & Acceptance Sprint

## Operating Model

This sprint is evidence-first. It freezes and describes the current system instead of expanding it.

The work has three lanes:

1. Documentation closure: reconcile workflow statuses and write final boundary/backlog/handoff documents.
2. Acceptance and audit: run local validation, inspect routes/contracts/security exposure, and produce quality findings.
3. Reproducibility: test a fresh setup in an isolated directory and record setup gaps.

## Scope Control

If a P0 or P1 issue is found, this sprint records it only. Repair work requires a separate user-approved task list.

No task may introduce:

- New business features.
- New migrations or database tables.
- AI Gateway refactors.
- Prompt admin, A/B testing, hot updates, or Prompt evaluation platform.
- Real provider probe or automatic circuit breaker.
- Recommendation algorithm changes.
- Formal acceptance based on `AUTH_BYPASS`.

## Document Strategy

Sprint-local reports live under:

```text
docs/workflows/system-freeze-acceptance-sprint/
```

Long-lived final docs live at:

```text
docs/final-system-boundary.md
docs/final-backlog.md
docs/final-handoff.md
```

Supporting screenshots, logs, and browser artifacts should live under:

```text
docs/workflows/system-freeze-acceptance-sprint/assets/
```

## Audit Strategy

The quality audit should prefer code facts over target-architecture claims. It should inspect the current implementation contracts around:

- Backend permissions and admin-only APIs.
- Public API filtering and leakage risk.
- AI output sanitization and formal entity write boundaries.
- `ai_call_logs` versus `ai_runs` responsibilities.
- Human accept/reject behavior.
- Review queue contracts.
- Attachment `storage_key` exposure.
- Migration upgrade/downgrade safety.
- Frontend AuthGate coverage for `/manage`.
- Public route admin-entry leakage.
- AI admin panel sensitive-field handling.
- Loading, error, empty, 404, and deprecated route states.
- Prompt Registry / Routing Policy responsibility split.
- Fallback chain explainability.
- Usage/cost/health truthfulness.
- Test skips, xfails, shared DB fragility, and warnings.

## Acceptance Strategy

Command validation should run against the current repo first. Browser validation should use local servers and must distinguish:

- Anonymous public access.
- Anonymous management denial.
- Authenticated management access.
- Sensitive field non-exposure.

If authentication setup blocks browser verification, record the blocker and do not substitute `AUTH_BYPASS` as formal proof.

## Fresh Setup Strategy

The fresh setup experiment should use a clean isolated path and avoid relying on existing local databases, `.env` files, or server state. It should record the exact manual steps needed to boot the system and distinguish hard blockers from optional provider-key limitations.

## Completion Criteria

The sprint is complete when all approved `tasks.md` items are either completed or explicitly blocked with evidence, validation is recorded, final docs are written, and the final daily-use recommendation is stated.
