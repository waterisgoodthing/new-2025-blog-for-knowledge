# Temporary Admin Bootstrap

## Goal

Add a safe code-level path to create or rotate a high-privilege temporary management account for this personal knowledge/blog backend.

## Touched Domains

- `auth`
- `manage`
- backend infrastructure

## Architectural Line

This task affects the personal knowledge backend under `backend/`. It should not change the original static-blog frontend under `src/` unless validation later proves a frontend login contract needs a small matching update.

## Current Status

Implemented and locally validated. A temporary admin account was created in the configured backend database on 2026-06-23.

## Workflow Files

- [Design](./design.md)
- [Requirements](./requirements.md)
- [Tasks](./tasks.md)
- [Validation](./validation.md)
- [Handoff Prompt](./handoff-prompt.md)
