# Batch 7 Compatibility And Closure

## Goal

完成 MVP 最后一批的兼容与收口设计：核对旧入口、公开读取、管理权限、基础状态、死链接和本地试运行边界，不进行大规模公开站重构、自动迁移或云部署。

## Current Status

Status: Batch 7 accepted; P0-02 through P0-06 completed. Stop here and do not start Batch 8 automatically.

## Touched Domains

- public route compatibility
- private manage route access
- legacy write/mistake entry points
- public/admin data visibility
- local validation and handoff documentation

## Hard Boundaries

- No new domain, database table, migration, cloud deployment, or bulk data migration.
- No deletion of old content or automatic rewrite of Note, Question, Mistake, Review, or Attachment rows.
- No Batch 8+ Capture/OCR/AI implementation.
- Public pages remain public; private writes, uploads, AI, and review remain backend-admin protected.
- Batch 7 must stop after acceptance and must not start another batch automatically.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [audit.md](./audit.md)
- [tasks.md](./tasks.md)
- [validation-plan.md](./validation-plan.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
