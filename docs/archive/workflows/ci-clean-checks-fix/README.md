# CI Clean Checkout Fix

## Goal

Make the GitHub Actions CI workflow pass from a clean checkout by removing its dependency on ignored generated type files and by migrating its disposable PostgreSQL database before tests.

## Touched Domain

Shared infrastructure: `.github/workflows/ci.yml` and root TypeScript declarations. No blog, notes, mistakes, review, auth, sync, home, share, or manage product behavior changes.

## Status

Planned. Root causes were verified from GitHub Actions run `30696127193`; implementation awaits approval of [tasks.md](./tasks.md).

## Workflow Files

- [Design](./design.md)
- [Requirements](./requirements.md)
- [Tasks](./tasks.md)
- [Validation](./validation.md)
