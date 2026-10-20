# Batch 5 Attachments

## Goal

建立私有学习系统的基础附件能力：管理员上传本地附件、查看元数据、受控预览/下载，并将附件关联到既有 QuestionDraft、Question 或 Mistake。

## Current Status

Status: P0-02 through P0-08 implemented, validated, and accepted. Batch 5 is closed; Batch 6 has started in a separate workflow.

## Touched Domains

- private attachment system
- manage attachments routes
- backend admin attachment APIs
- existing Question/Mistake link compatibility

## Hard Boundaries

- No OCR, Capture, AI processing, PDF parsing, upload to R2/object storage, Practice, Search, Analytics, or public attachment delivery.
- No replacement or migration of existing attachment rows or Note data.
- `AuthGate` is page-level UX only; backend `get_current_admin` remains the security boundary.
- Batch 5 implementation is closed. Batch 6 work is tracked only in its separate workflow.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [schema-design.md](./schema-design.md)
- [api-contract.md](./api-contract.md)
- [audit.md](./audit.md)
- [tasks.md](./tasks.md)
- [validation-plan.md](./validation-plan.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
