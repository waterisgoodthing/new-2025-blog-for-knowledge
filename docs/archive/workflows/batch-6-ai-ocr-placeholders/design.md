# Design

## Page Responsibilities

### `/manage/ai`

AI governance entry point only. Show capability status, disabled state, and the boundary between future assistance and current manual workflows. Do not show fabricated provider health, model availability, cost, or run counts.

### `/manage/ai/runs`

Audit surface placeholder only. It may explain that run history is not part of this batch. It must not query existing `ai_runs` or `ai_call_logs` as if Batch 6 were implementing a new audit workflow.

### `/manage/capture`

OCR/Capture entry point placeholder only. It must not upload files, invoke recognition, classify content, create drafts, or mutate attachment status. Existing Batch 5 attachment upload remains the only upload capability.

### Attachment OCR Status

The existing attachment detail explanation may remain informational. Any status label must be static and must not imply that OCR is queued, running, completed, or failed.

## Component Boundary

Use shared manage presentation components for `ManagePageHeader`, `EmptyState`, `StatusBadge`, and future-capability messaging. Route pages compose UI only. No API calls from placeholder components.

## Permission Boundary

All three pages live under the protected manage workspace. This is a page-access experience only. If a future API is introduced, it must independently use backend `get_current_admin`.

## Existing-Code Reconciliation

The worktree currently contains Capture and AI-related backend modules and client/component files, and the database contains historical `capture_items`, `ai_call_logs`, and `ai_runs` rows. Their presence does not authorize Batch 6 behavior. Batch 6 must preserve them and avoid invoking, expanding, or migrating them.
