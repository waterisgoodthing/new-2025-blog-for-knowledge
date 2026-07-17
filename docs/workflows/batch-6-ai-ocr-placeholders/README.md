# Batch 6 AI And OCR Placeholders

## Goal

建立管理端 AI/OCR 能力的清晰占位、状态表达和未来接口边界，不接入真实模型、OCR、Prompt 管理、调用持久化或任务队列。

## Current Status

Status: P0-01 through P0-06 implemented, validated, and accepted. Batch 6 is closed; Batch 7 has not started.

## Touched Domains

- private manage AI placeholder pages
- private manage Capture/OCR placeholder page
- existing Attachment status/metadata presentation
- future AI/OCR contract documentation only

## Hard Boundaries

- No provider call, OCR execution, AI prompt execution, AI result persistence, job queue, capture routing, automatic draft creation, or business-data mutation.
- No migration, new table, model change, or public AI/OCR API.
- Existing `ai_call_logs`, `ai_runs`, `capture_items`, attachments, Questions, Mistakes, and Notes are not rewritten or reinterpreted.
- `AuthGate` and backend `get_current_admin` remain required for private manage surfaces; frontend placeholders are not security.
- Batch 6 is closed. Batch 7 requires a separate design package, audit, task list, and explicit approval.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [api-contract.md](./api-contract.md)
- [audit.md](./audit.md)
- [tasks.md](./tasks.md)
- [validation-plan.md](./validation-plan.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
