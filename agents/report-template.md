# Result Report Template

## Conclusion

`PASS | PARTIAL | FAIL | BLOCKED | NOT_VERIFIED | NOT_AUTHORIZED`

State the outcome first. Briefly state execution mode and routing reason; distinguish final code accept from task status and user authorization.

## Changes

List only actual changes.

## Evidence

Provide relevant paths, current-source facts, or runtime/data evidence. For `WORKER`, identify actual executor/reviewer/verifier assignments and their outputs; distinguish planned, executed, and unavailable assignments.

## Verification

List checks and results. Distinguish simulated, real-browser, isolated-database, and production evidence.

## Main Agent Acceptance

For non-simple work, record accepted, rework required, or not accepted with the reason: scope/acceptance checks, actionable findings and their resolution, verification, and required gate results. Simple work may state acceptance alongside the conclusion. Final accept does not imply commit, push, merge, migration, deployment, or production writes.

## Risks / Remaining / Decision Needed

State remaining risks, deferred or unexecuted work, and the exact decision required. Omit empty sections when a shorter report is clearer.

