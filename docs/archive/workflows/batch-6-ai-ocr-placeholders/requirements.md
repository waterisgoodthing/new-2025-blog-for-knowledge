# Requirements

## In Scope

1. `/manage/ai` clearly communicates that AI execution is not enabled.
2. `/manage/ai/runs` clearly communicates that no new run history is created by Batch 6.
3. `/manage/capture` clearly communicates that OCR/Capture is reserved and unavailable.
4. Existing attachment detail surfaces may show OCR readiness as a non-actionable status, without starting processing.
5. Placeholder states include unavailable, empty, error, and future-capability boundaries without fake metrics or fake results.
6. Route-level `AuthGate` remains in effect through the manage workspace; no public route is changed.

## Explicitly Out Of Scope

- Real AI provider calls or model selection.
- OCR, PDF parsing, image recognition, Capture Router classification, or automatic draft creation.
- Prompt templates, prompt versions, AI result storage, cost accounting, retries, jobs, queues, webhooks, streaming, or background workers.
- New database tables, migrations, API endpoints, persistence fields, object storage, search, analytics, Practice, or Review changes.

## Acceptance

- Placeholder pages render from static state or existing non-mutating shell components.
- No placeholder page calls an AI, OCR, Capture, Job, or admin run API.
- Existing public pages remain unchanged and do not request admin AI/OCR APIs anonymously.
- No database revision or row count changes occur.
