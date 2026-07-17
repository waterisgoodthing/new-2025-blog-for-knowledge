# Public Mistake Review API Gate

## Goal

验证公开 `/mistakes` 页面在匿名访问时不会请求管理员复习统计或复习计划 API，并保留管理员登录后的复习摘要能力。

## Current Status

Status: P0-01 through P0-05 implemented, validated, and accepted. Workflow closed; Batch 7 remains separate.

## Touched Domains

- public mistakes page
- shared review hooks
- frontend permission regression tests

## Hard Boundaries

- No backend changes, database changes, migrations, or API contract changes.
- No conditional Hook calls that violate React Rules of Hooks.
- No changes to public Note visibility or `/mistakes` content filtering.
- No changes to Batch 5/6. This workflow is closed and does not authorize Batch 7.

## Workflow Files

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
