# System Freeze & Acceptance Sprint

## Task Goal

Freeze the current post-Batch-12 system, reconcile workflow status, run a complete local acceptance pass, audit quality risks, test fresh setup reproducibility, and produce final handoff material for deciding whether the system can enter real daily use.

This sprint is a closure and acceptance sprint. It must not add business features, migrations, database tables, AI Gateway refactors, Prompt admin, A/B testing, provider probes, circuit breakers, recommendation changes, or automatic fixes for newly discovered issues.

## Touched Domains

- `docs/workflows`: workflow status cleanup and sprint evidence.
- `docs`: final system boundary, final backlog, and final handoff.
- `backend`: read-only audit and validation commands only unless a later repair task is explicitly approved.
- `src`: read-only audit and validation commands only unless a later repair task is explicitly approved.
- `manage`, `ai`, `auth`, `review`, `mistakes`, `attachments`, and shared infrastructure: inspected for acceptance and quality review.

## Current Status

Status: `completed`.

The repository has a large pre-existing dirty worktree. This sprint preserved unrelated user and generated changes. The task list in `tasks.md` was explicitly approved before execution.

## Workflow Files

- [Requirements](requirements.md)
- [Design](design.md)
- [Tasks](tasks.md)
- [Validation](validation.md)
- [Audit](audit.md)
- [Diff Report](diff-report.md)
- [Final Decision](final-decision.md)
- [Handoff Prompt](handoff-prompt.md)

## Planned Outputs

- Task status cleanup report.
- `docs/final-system-boundary.md`.
- Complete local acceptance results.
- `docs/final-backlog.md`.
- Codex quality audit report with P0/P1/P2/P3 findings.
- Fresh setup report from an isolated path.
- `docs/final-handoff.md`.
- Final recommendation: A, B, or C for real daily use.
